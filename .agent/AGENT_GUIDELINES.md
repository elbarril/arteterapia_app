# Agent Guidelines - Arteterapia Application

**Version:** 1.0  
**Last Updated:** December 2025  
**Project Type:** Flask Web Application for Art Therapy Workshop Management

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Project Structure](#project-structure)
4. [Development Standards](#development-standards)
5. [Database & Models](#database--models)
6. [Authentication & Security](#authentication--security)
7. [Internationalization (i18n)](#internationalization-i18n)
8. [Frontend Guidelines](#frontend-guidelines)
9. [Testing & Debugging](#testing--debugging)
10. [Common Workflows](#common-workflows)
11. [Important Context](#important-context)

---

## Project Overview

### Purpose
Arteterapia is a complete Flask-based web application designed for **art therapists** to manage workshops, sessions, participants, and therapeutic observational records. The application focuses on providing a minimalist, clean interface for systematic therapeutic observation using a structured question-based approach.

### Key Features
- **Workshop Management**: Create and manage art therapy workshops with objectives
- **Participant Tracking**: Add and manage participants for each workshop
- **Session Planning**: Define sessions with prompts, motivations, and materials
- **Observational Records**: Step-by-step therapeutic observation flow with 8 comprehensive categories and ~50 questions
- **Consolidated Reporting**: View all observations in a structured table format
- **Admin Interface**: Full CRUD operations via Flask-Admin (restricted to admin role)
- **Role-based Authentication**: Admin and Editor roles with invitation-based registration
- **Database Portability**: SQLAlchemy + Alembic for easy database migration

### Target Users
- **Art Therapists (Primary)**: Managing workshops, sessions, participants, and observations
- **Administrators**: User management, system configuration, data correction

---

## Architecture & Technology Stack

### Backend
- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy (v3.1.1)
- **Migrations**: Flask-Migrate 4.0.5 (Alembic)
- **Admin Panel**: Flask-Admin 1.6.1
- **Authentication**: Flask-Login 0.6.3
- **Email**: Flask-Mail 0.9.1
- **Configuration**: python-dotenv 1.0.0

### Frontend
- **CSS Framework**: Bootstrap 5
- **Bootstrap Integration**: Bootstrap-Flask 2.3.3
- **JavaScript**: Vanilla JS with AJAX for dynamic interactions
- **Templating**: Jinja2 (Flask default)

### Database
- **Development**: SQLite (`arteterapia.db`)
- **Production Ready**: PostgreSQL or MySQL (via SQLAlchemy)

### Design Philosophy
- **Minimalist Design**: Clean interface with semantic button hierarchy
- **Brand Colors**: Applied to borders, icons, and shadows (not action-based)
- **Responsive**: Mobile-first design with Bootstrap 5
- **Accessible**: Focus states and keyboard navigation
- **Scalable**: Modular architecture for easy extension

---

## Project Structure

```
arteterapia_app/
├── .agent/                       # Agent documentation (this directory)
│   ├── AGENT_GUIDELINES.md       # This file - comprehensive guide
│   └── workflows/                # Workflow documentation
├── .venv/                        # Virtual environment (ignored in git)
├── app/                          # Main application package
│   ├── __init__.py               # Flask application factory
│   ├── admin_views.py            # Custom Flask-Admin views with security
│   ├── controllers/              # Route handlers and business logic (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication routes (login, register, etc.)
│   │   ├── language.py           # Language switcher routes
│   │   ├── observation.py        # Observation recording routes
│   │   ├── participant.py        # Participant CRUD routes
│   │   ├── session.py            # Session CRUD routes
│   │   └── workshop.py           # Workshop CRUD and listing routes
│   ├── models/                   # SQLAlchemy data models
│   │   ├── __init__.py
│   │   ├── observation.py        # ObservationalRecord model
│   │   ├── observation_questions.py  # Question structure, VERY IMPORTANT
│   │   ├── participant.py        # Participant model
│   │   ├── role.py               # Role model (Admin, Editor)
│   │   ├── session.py            # Session model
│   │   ├── user.py               # User model with authentication methods
│   │   ├── user_invitation.py    # UserInvitation model for registration
│   │   └── workshop.py           # Workshop model
│   ├── static/                   # Static assets
│   │   ├── css/
│   │   │   └── custom.css        # Custom minimalist design
│   │   └── js/
│   │       └── app.js            # AJAX interactions and dynamic behaviors
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html             # Base template with navbar
│   │   ├── auth/                 # Authentication templates
│   │   │   ├── change_password.html
│   │   │   ├── create_invitation.html
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── observation/          # Observation templates
│   │   │   ├── record.html       # Step-by-step observation flow
│   │   │   └── view_all.html     # Consolidated table view
│   │   └── workshop/             # Workshop templates
│   │       ├── detail.html       # Workshop detail with participants and sessions
│   │       └── list.html         # Workshop listing
│   └── utils/                    # Utility modules
│       └── email_utils.py        # Email sending utilities
├── migrations/                   # Alembic database migrations
│   └── versions/                 # Migration version files
├── .env                          # Environment variables (ignored in git)
├── .env.example                  # Example environment configuration
├── .gitignore                    # Git ignore rules
├── config.py                     # Application configuration classes
├── README.md                     # User-facing documentation
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
└── setup_db.py                   # Database setup script (with sample data option)
```

### Key File Roles

#### Core Application Files
- **`run.py`**: Application entry point, creates Flask app and runs dev server
- **`config.py`**: Configuration classes (Development, Production) with all settings
- **`app/__init__.py`**: Application factory, extension initialization, blueprint registration

#### Models (app/models/)
- **`observation_questions.py`**: **CRITICAL** - Contains the entire therapeutic question structure
- **`observation.py`**: Stores observation records with JSON answers
- **`user.py`**: User authentication, password hashing, role checking
- **`workshop.py`, `session.py`, `participant.py`**: Core entity models

#### Controllers (app/controllers/)
- Each blueprint handles routes for a specific domain
- Follow RESTful naming conventions where applicable
- All routes (except auth) require `@login_required` decorator

#### Templates
- **`base.html`**: Master template with navbar, flash messages
- All templates extend `base.html`

---

## Development Standards

### Code Style
- **Python**: Follow PEP 8 conventions
- **Naming**: 
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Docstrings**: Use for all classes and non-trivial functions
- **Comments**: Explain "why", not "what"

### Flask Best Practices
1. **Use Application Factory Pattern**: Already implemented in `app/__init__.py`
2. **Blueprints for Modular Routes**: One blueprint per domain (workshop, participant, etc.)
3. **Environment-based Configuration**: Use `config.py` classes, never hardcode
4. **Extension Initialization**: Initialize extensions globally, then call `init_app()` in factory
5. **Database Sessions**: Use `db.session` for all database operations
6. **Flash Messages**: Use categories: `success`, `info`, `warning`, `danger`

### Git Workflow
- **Branch Naming**: Descriptive names like `feature/invitation-system` or `fix/language-switcher`
- **Commits**: Granular, descriptive commits for each logical change
- **Branch Strategy**: **ALWAYS** create a new branch for changes. **NEVER** commit directly to `master`.
- **Never Commit**: `.env`, `*.db`, `__pycache__`, `.venv`

### Command Execution (CRITICAL)
- **Virtual Environment**: ALWAYS active the virtual environment or access binaries directly from `.venv` before running Python commands.
  - **Windows Powershell**: `.\.venv\Scripts\Activate.ps1; python script.py` OR `.\.venv\Scripts\python.exe script.py`
  - **Git Bash/Unix**: `source .venv/bin/activate && python script.py` OR `.venv/bin/python script.py`
- **Dependency Management**: Ensure all new dependencies are installed in the venv and added to `requirements.txt`.

### Error Handling
- Always wrap database operations in try-except blocks
- Log errors appropriately
- Use flash messages to inform users of issues
- Return meaningful HTTP status codes

---

## Database & Models

### Database Configuration
- **Development**: SQLite at `arteterapia.db` (gitignored)
- **Connection String**: Set via `DATABASE_URL` in `.env` or defaults to SQLite
- **Migrations**: Alembic via Flask-Migrate

### Model Relationships

```
User ──┬─> Role (many-to-many via user_roles)
       └─> UserInvitation (one-to-many)

Workshop ──┬─> Session (one-to-many)
           └─> Participant (one-to-many)

Session ──> ObservationalRecord (one-to-many)
Participant ──> ObservationalRecord (one-to-many)
```

### Critical Models

#### ObservationalRecord
- **Purpose**: Stores therapeutic observations with structured questions
- **Key Fields**:
  - `answers` (JSON): Stores all question responses as `{question_id: answer_value}`
  - `notes` (Text): Freeform therapist notes
  - Relationships: `session_id`, `participant_id`, `workshop_id`
- **Important**: Question IDs must match those in `observation_questions.py`

#### User
- **Purpose**: Authentication and authorization
- **Key Methods**:
  - `set_password(password)`: Hash and store password
  - `check_password(password)`: Verify password
  - `is_admin()`: Check if user has admin role
  - `generate_verification_token()`, `verify_email_token()`: Email verification
- **Flask-Login Integration**: Implements required methods (`is_authenticated`, etc.)

### Observation Questions Structure
Located in `app/models/observation_questions.py`:

**8 Main Categories** (some with subcategories):
1. **INGRESO AL ESPACIO** (Entry into the Space) - 4 questions
2. **MOTIVACIÓN** (Motivation) - 3 questions
3. **CONSIGNA** (Instruction) - 5 questions
4. **DESARROLLO** (Development) - 5 subcategories:
   - Inicio (Beginning)
   - Tiempo (Time)
   - Materiales (Materials)
   - Creatividad (Creativity)
   - En el espacio (In the space)
5. **CIERRE** (Closure) - 6 questions
6. **GRUPO** (Group) - 5 questions
7. **CLIMA GRUPAL** (Group Climate) - 4 questions

**Total**: ~50 questions

**Answer Options**:
- `yes`: Sí
- `no`: No
- `not_sure`: No está seguro/a
- `not_applicable`: No aplica

### Database Operations

#### Creating Database
```bash
# Initial setup with admin user only
python setup_db.py

# Setup with sample data (recommended for development)
python setup_db.py --with-data

# Reset database (WARNING: deletes all data)
python setup_db.py --reset
python setup_db.py --reset --with-data
```

#### Migrations
```bash
# Create migration after model changes
flask --app run db migrate -m "Description of changes"

# Apply migrations
flask --app run db upgrade

# Rollback migration
flask --app run db downgrade
```

---

## Authentication & Security

### Authentication Flow

#### User Registration (Invitation-Based)
1. **Admin** creates invitation via `/auth/create-invitation` (POST with email)
2. System generates unique token and sends email with registration link
3. **User** clicks link, fills registration form at `/auth/register/<token>`
4. System creates user account, sends verification email
5. **User** verifies email via link
6. **User** can now log in

#### Login Flow
1. User submits credentials at `/auth/login`
2. System verifies password hash
3. If valid, Flask-Login creates session
4. User redirected to workshop list

#### Password Reset
1. User requests reset at `/auth/forgot-password`
2. System sends password reset email with token
3. User sets new password at `/auth/reset-password/<token>`
4. System updates password hash

### Security Best Practices

#### CRITICAL: Always Verify in Code
- **Never trust client-side checks**: Always verify permissions on the server
- **Use decorators**: `@login_required` on all protected routes
- **Role checks**: Use `current_user.is_admin()` for admin-only features

#### Password Security
- **Hashing**: Uses Werkzeug's `generate_password_hash` with default settings (pbkdf2:sha256)
- **Minimum Length**: 6 characters (configurable in code)
- **Never log passwords**: Never print or log password values

#### Token Security
- **Password Reset**: Expires after 24 hours (configurable in `config.py`)
- **Email Verification**: Expires after 24 hours
- **Invitations**: Expire after 7 days
- **Implementation**: Uses `itsdangerous.URLSafeTimedSerializer` with `SECRET_KEY`

#### Environment Variables
```bash
# CRITICAL: Never commit .env file
SECRET_KEY=<64-character random hex>  # Generate: python -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=sqlite:///arteterapia.db  # Or PostgreSQL/MySQL in production
MAIL_SERVER=smtp.example.com
MAIL_USERNAME=...
MAIL_PASSWORD=...  # Use app-specific passwords for Gmail
```

### User Roles

#### Admin
- Full access to all features
- Access to Flask-Admin panel (`/admin`)
- Can create user invitations
- Can modify any data

#### Editor
- Can manage workshops, participants, sessions, observations
- Cannot access Flask-Admin panel
- Cannot create user invitations

### Route Protection Examples

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

---

## Frontend Guidelines

### CSS Architecture

#### Design System (`app/static/css/custom.css`)
```css
:root {
    /* Brand colors - borders, icons, shadows */
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --tertiary-color: #94a3b8;
    --accent-color: #3b82f6;
    --accent-shadow: rgba(37, 99, 235, 0.1);
    
    /* Neutral palette */
    --bg-light: #f8fafc;
    --border-light: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
}
```

#### Key Principles
1. **Semantic Button Hierarchy**: Not action-based (create = primary, secondary actions = outline)
2. **Brand Colors**: Used for borders, shadows, and accents—not fill colors unless primary action
3. **Minimalist**: Clean, uncluttered, with generous whitespace
4. **Micro-animations**: Subtle transitions for better UX (hover, expand/collapse)

#### Component Classes
- `.workshop-card`: Workshop listing cards with hover effects
- `.session-card`: Expandable session cards
- `.observation-card`: Observation recording interface
- `.answer-btn`: Answer option buttons with visual feedback
- `.btn-create-workshop`: Floating action button with + icon

### JavaScript Patterns (`app/static/js/app.js`)

#### AJAX Form Submission
```javascript
// Example: Update workshop objective
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

#### Dynamic Interactions
- **Inline Editing**: Workshop objectives editable on click
- **Session Expansion**: Click to expand/collapse session details
- **Answer Selection**: Visual feedback on observation question answers

### Bootstrap 5 Guidelines
- **Use utility classes**: `mb-3`, `mt-4`, `d-flex`, `justify-content-between`
- **Responsive breakpoints**: `col-md-6`, `col-lg-4`
- **Components**: Cards, modals, badges, alerts, list groups
- **Icons**: Currently using text symbols (`+`, `▼`), can integrate Bootstrap Icons if needed
- **Modals vs Native Alerts**: **NEVER** use native `alert()`, `confirm()`, or `prompt()`. Use the `showModal` helper (in `app.js`) with Bootstrap modals for all user interactions.

### Template Structure

#### Base Template (`base.html`)
All pages extend this template:
```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}
```

#### Common Patterns
```html
<!-- Flash messages (included in base.html) -->
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<!-- Form with CSRF protection -->
<form method="POST">
    {{ form.hidden_tag() }}  <!-- If using Flask-WTF -->
    <!-- OR -->
    <!-- If using manual forms, CSRF is auto-included by Flask -->
</form>
```

---

## Testing & Debugging

### Running the Application

#### Development Mode
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run development server
python run.py
```

The app will be available at:
- Main app: `http://localhost:5000` or `http://127.0.0.1:5000`
- Admin panel: `http://localhost:5000/admin`

#### Configuration Check
- Verify `.env` file exists and has correct values
- Check console output for startup errors
- Confirm database file exists (`arteterapia.db`)

### Debugging Techniques

#### Flask Debug Mode
- Set `FLASK_ENV=development` in `.env`
- Enables:
  - Auto-reload on code changes
  - Detailed error pages with stack traces
  - Console logging

#### Email Debugging
- In development, emails are printed to console if `MAIL_SUPPRESS_SEND=true`
- Check terminal output for email content
- For testing actual sending, use Mailtrap or similar service

#### Database Inspection
```bash
# Using sqlite3 command-line tool
sqlite3 arteterapia.db

# Common queries
.tables  # List all tables
SELECT * FROM users;
SELECT * FROM workshops;
.schema observational_records
```

#### Logging
```python
# Add to any route for debugging
import logging
logging.debug(f"Debug info: {variable}")
print(f"[DEBUG] Variable value: {variable}")  # Appears in console
```

### Common Issues

#### 1. Database Locked Error (SQLite)
- Stop all running Flask instances
- Close any database browser tools
- Restart application

#### 2. 404 on Routes
- Verify blueprint is registered in `app/__init__.py`
- Check route definition matches URL
- Ensure `@login_required` decorator is applied if needed

#### 3. Flash Messages Not Appearing
- Check `base.html` includes flash message block
- Verify `flash()` is called before `redirect()`
- Confirm correct category name used

---

## Common Workflows

### Adding a New Feature

1. **Plan**: Identify models, routes, and templates needed
2. **Models**: Update/create models in `app/models/`
3. **Migration**: `flask --app run db migrate -m "Add feature X"`
4. **Apply**: `flask --app run db upgrade`
5. **Controller**: Add routes to appropriate blueprint in `app/controllers/`
6. **Template**: Create/update templates in `app/templates/`
7. **Test**: Manual testing in browser
8. **Commit**: Granular commits with descriptive messages

### Modifying Observation Questions

**IMPORTANT**: Questions are defined in `app/models/observation_questions.py`

To add/modify questions:
1. Edit `OBSERVATION_CATEGORIES` list
2. Update translations extraction
3. Recompile translations
4. Existing observations continue to work (backward compatible)

**DO NOT** change question IDs if observations already exist, as this will break existing data.

### Changing UI Styles

1. Edit `app/static/css/custom.css`
2. Use CSS variables for brand colors
3. Maintain semantic button hierarchy
4. Test responsive behavior (`@media` queries)
5. Verify accessibility (focus states, contrast)

### Database Reset (Development)

```bash
# WARNING: This deletes all data
python setup_db.py --reset --with-data

# Restart Flask application
# (Stop with Ctrl+C, then run python run.py again)
```

---

## Important Context

### Recent Development History

Based on recent conversation summaries:

1. **Internationalization System**: Recently implemented with Spanish (default) and English
2. **Language Switcher**: Fixed and functional, controlled by `ENABLE_LANGUAGE_SWITCH` config flag
3. **Authentication System**: Invitation-based registration fully tested and verified
4. **Flask-Admin**: All CRUD operations functional with proper role-based access control
5. **Repository Cleanup**: `.gitignore` properly configured, unnecessary files removed

### Known Decisions

1. **Default Language**: Spanish—do not change without user request
2. **Minimalist Design**: Avoid adding heavy UI frameworks or complex animations
3. **Database Choice**: SQLite for development is intentional; production can use PostgreSQL/MySQL
4. **Question Structure**: Fixed therapeutic framework from domain experts—do not modify without explicit request
5. **Role Model**: Two roles (Admin, Editor) sufficient for use case

### User Preferences

From conversation history:
- User prefers **descriptive Git commits** with granular changes
- User values **comprehensive documentation**
- User wants to avoid icons in documentation or code or commits messages
- User expects **systematic approach** to development tasks
- User likes to **review changes** before major actions

### Future Considerations

Potential areas for expansion (not currently implemented):
- PDF export of consolidated observations
- Email notifications for new observations
- Advanced search/filtering in observations table
- Workshop templates for common session structures
- User profile management
- Data analytics/visualization of observation trends

---

## Quick Reference

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **⚠️ Change immediately after first login**

### Key Routes
- `/` → Workshop list (login required)
- `/auth/login` → Login page
- `/auth/create-invitation` → Create user invitation (admin only)
- `/workshop/<id>` → Workshop detail
- `/admin` → Flask-Admin panel (admin only)
- `/lang/<code>` → Switch language

### Configuration Flags
- `ENABLE_LANGUAGE_SWITCH`: Show/hide language switcher in UI
- `BABEL_DEFAULT_LOCALE`: Default application language
- `MAIL_SUPPRESS_SEND`: Log emails to console instead of sending

### Essential Commands
```bash
# Setup database
python setup_db.py --with-data

# Run application
python run.py

# Create migration
flask --app run db migrate -m "Message"

# Apply migration
flask --app run db upgrade

# Compile translations
pybabel compile -d translations
```

---

## Frontend Architecture

### Overview
The frontend follows modern best practices with **Atomic Design CSS**, **Object-Oriented JavaScript**, and **comprehensive accessibility** (WCAG 2.1 AA compliant).

### CSS Architecture - Atomic Design

**Location**: `app/static/css/`

The CSS is organized using Atomic Design methodology for maximum maintainability and reusability:

```
css/
├── main.css                    # Main aggregator (imports all modules)
├── tokens/
│   └── variables.css           # Design tokens (colors, spacing, typography, shadows)
├── atoms/                      # Basic building blocks
│   ├── typography.css          # Text styles
│   ├── buttons.css             # Button styles
│   ├── forms.css               # Form control styles
│   └── badges.css              # Badge styles
├── molecules/                  # Simple components
│   ├── cards.css               # Card components
│   ├── modals.css              # Modal dialogs
│   ├── lists.css               # List groups
│   ├── tables.css              # Table styles
│   └── progress.css            # Progress bars
├── organisms/                  # Complex components
│   ├── navbar.css              # Navigation bar
│   ├── workshop.css            # Workshop-specific components
│   ├── session.css             # Session cards and interactions
│   └── observation.css         # Observation flow components
└── utilities/                  # Helper classes
    ├── animations.css          # Transition timing
    └── accessibility.css       # Focus states, sr-only class
```

**Design Tokens** (`tokens/variables.css`):
- Brand colors (primary, secondary, accent)
- Spacing scale (xs, sm, md, lg, xl)
- Typography (font families, sizes, weights)
- Border radius values
- Shadow definitions
- Transition timings

**Usage**:
```css
/* Use design tokens instead of hard-coded values */
.my-component {
    color: var(--primary-color);
    padding: var(--spacing-md);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
}
```

### JavaScript Architecture - OOP Modules

**Location**: `app/static/js/`

The JavaScript follows Object-Oriented Programming with modular architecture:

```
js/
├── app.js                      # Application initializer
├── core/                       # Core utilities
│   ├── api-client.js           # APIClient class (centralized AJAX)
│   └── modal-manager.js        # ModalManager class (Bootstrap modals)
└── modules/                    # Feature modules
    ├── workshop-detail.js      # WorkshopDetailManager + sub-managers
    └── observation.js          # ObservationFlow class
```

#### Core Modules

**APIClient** (`core/api-client.js`):
```javascript
// Centralized AJAX request handler
const apiClient = new APIClient();

// Usage
const data = await apiClient.post('/endpoint', { key: 'value' });
```

**ModalManager** (`core/modal-manager.js`):
```javascript
// Bootstrap modal wrapper
const modalManager = new ModalManager();

// Usage
await modalManager.alert('Message');
const confirmed = await modalManager.confirm('Are you sure?');
const value = await modalManager.prompt('Enter value:', 'default');
```

#### Feature Modules

**WorkshopDetailManager** (`modules/workshop-detail.js`):
- Manages all interactions on workshop detail page
- Uses event delegation (no inline onclick handlers)
- Sub-managers:
  - `ObjectiveManager`: Edit workshop objective
  - `ParticipantManager`: CRUD operations for participants
  - `SessionManager`: CRUD operations for sessions

**ObservationFlow** (`modules/observation.js`):
- Manages step-by-step observation recording
- Handles question progression
- Highlights previously answered questions
- Submits answers via APIClient

#### Application Initialization

**app.js**:
```javascript
// Detects current page and initializes appropriate manager
function initializePage() {
    const path = window.location.pathname;
    
    if (path.match(/^\/workshop\/\d+$/)) {
        new WorkshopDetailManager(workshopId);
    }
    
    if (path.match(/^\/session\/\d+\/observe\/\d+$/)) {
        new ObservationFlow(observationConfig);
    }
}
```

### Template Architecture

**Zero Inline JavaScript**: All templates use `data-action` attributes instead of `onclick`:

```html
<!-- OLD (removed) -->
<button onclick="deleteItem(123)">Delete</button>

<!-- NEW (current) -->
<button data-action="delete-item" data-item-id="123">Delete</button>
```

**Event Delegation**: JavaScript modules listen for clicks on parent elements:

```javascript
document.addEventListener('click', (e) => {
    const deleteBtn = e.target.closest('[data-action="delete-item"]');
    if (deleteBtn) {
        const id = deleteBtn.dataset.itemId;
        this.delete(id);
    }
});
```

### Accessibility Features

**ARIA Attributes**:
- `aria-label`: Descriptive labels for all interactive elements
- `aria-hidden="true"`: Decorative icons hidden from screen readers
- `aria-expanded`, `aria-controls`: For collapsible elements
- `aria-valuenow`, `aria-valuemin`, `aria-valuemax`: For progress bars
- `role="button"`, `role="group"`: Semantic roles

**Keyboard Navigation**:
- `tabindex="0"`: Keyboard focusable elements
- Focus states: Visible outline for keyboard users
- Enter key support for custom interactive elements

**Screen Reader Support**:
- `.sr-only` class: Visually hidden but read by screen readers
- Proper heading hierarchy (h1 → h2 → h3)
- Semantic HTML5 elements (`<nav>`, `<section>`, `<article>`)

**Example**:
```html
<button data-action="toggle-session" 
        data-session-id="5"
        role="button"
        tabindex="0"
        aria-expanded="false"
        aria-controls="session5"
        aria-label="Expandir detalles de la sesión">
    <i class="bi bi-chevron-down" aria-hidden="true"></i>
</button>
```

### Testing Infrastructure

**Location**: `tests/`

```
tests/
├── conftest.py                 # Pytest fixtures (app, database, users)
├── unit/                       # Unit tests
├── integration/                # Integration tests
│   ├── test_workshop_routes.py
│   ├── test_participant_routes.py
│   ├── test_session_routes.py
│   └── test_observation_routes.py
└── e2e/                        # End-to-end tests (Selenium)
```

**Running Tests**:
```bash
# All tests
pytest -v

# Specific category
pytest tests/integration/ -v

# With coverage
pytest --cov=app tests/

# Specific markers
pytest -m unit
pytest -m integration
pytest -m e2e
```

**Test Fixtures** (in `conftest.py`):
- `app`: Test Flask application with in-memory SQLite
- `client`: Test client for making requests
- `db_session`: Database session with automatic cleanup
- `admin_user`, `editor_user`: Pre-created test users
- `workshop`, `participant`, `session_obj`: Test data
- `authenticated_client`: Client logged in as admin

### Frontend Development Guidelines

**CSS Best Practices**:
1. Always use design tokens from `variables.css`
2. Follow Atomic Design hierarchy (atoms → molecules → organisms)
3. Keep specificity low (avoid deep nesting)
4. Use BEM-like naming for custom classes
5. Maintain 100% visual compatibility when refactoring

**JavaScript Best Practices**:
1. Use ES6+ features (classes, async/await, arrow functions)
2. Keep modules focused (single responsibility)
3. Use event delegation instead of inline handlers
4. Always use `apiClient` for AJAX requests
5. Always use `modalManager` for alerts/confirms/prompts
6. Handle errors gracefully with try/catch

**Template Best Practices**:
1. NO inline JavaScript (use `data-action` attributes)
2. Add ARIA labels to ALL interactive elements
3. Mark decorative icons with `aria-hidden="true"`
4. Use semantic HTML5 elements
5. Maintain proper heading hierarchy
6. Add `sr-only` labels for form fields

**Accessibility Checklist**:
- [ ] All buttons have `aria-label`
- [ ] All icons have `aria-hidden="true"`
- [ ] Collapsible elements have `aria-expanded` and `aria-controls`
- [ ] Progress bars have `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- [ ] Form fields have visible or `sr-only` labels
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Focus states are visible
- [ ] Color contrast meets WCAG AA standards

### Performance Considerations

**CSS**:
- Modular files enable better browser caching
- Main.css imports all modules (single HTTP request in production)
- Design tokens reduce CSS duplication

**JavaScript**:
- Modules loaded in correct order (core → modules → app)
- Event delegation reduces memory usage
- Lazy initialization (only load managers for current page)

**Templates**:
- Server-side rendering (no client-side frameworks)
- Minimal JavaScript for fast initial load
- Progressive enhancement approach

---

## Additional Resources


- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://www.sqlalchemy.org/
- **Flask-Admin Documentation**: https://flask-admin.readthedocs.io/
- **Bootstrap 5 Documentation**: https://getbootstrap.com/docs/5.0/
- **Babel Documentation**: http://babel.pocoo.org/

---

## Document Maintenance

**When to Update This Document**:
- Major architectural changes
- New models or significant model changes
- New authentication/security mechanisms
- Changes to development workflow
- Addition of new technologies or frameworks
- Discovery of critical bugs or edge cases

**How to Update**:
1. Edit this file with clear, concise additions
2. Update "Last Updated" date at top
3. Increment version number if major changes
4. Commit with message: `docs: Update agent guidelines - [brief description]`

---

*This document is designed to provide AI agents with comprehensive context to work effectively on the Arteterapia project. It should be read in full before starting any significant work.*
