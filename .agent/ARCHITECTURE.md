# System Architecture

This document provides visual representations of the Arteterapia application architecture.

---

## Application Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Templates (Jinja2)          │  Static Assets                   │
│  ├─ base.html                │  ├─ CSS (custom.css)             │
│  ├─ auth/                    │  └─ JS (app.js)                  │
│  ├─ workshop/                │                                   │
│  └─ observation/             │  Bootstrap 5 + Vanilla JS        │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ROUTE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Flask Blueprints (app/routes/)                                  │
│  ├─ auth_bp         - Authentication (login, register, etc.)    │
│  ├─ workshop_bp     - Workshop CRUD + listing                   │
│  ├─ participant_bp  - Participant management                    │
│  ├─ session_bp      - Session management                        │
│  ├─ observation_bp  - Observation recording + viewing           │
│  └─ lang_bp         - Language switching                        │
│                                                                  │
│  Flask-Admin (admin_views.py)                                   │
│  └─ 7 Custom ModelViews with role-based access control          │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Extensions & Services                                           │
│  ├─ Flask-Login      - Session management, user loader          │
│  ├─ Flask-Mail       - Email sending (invitations, resets)      │
│  └─ Email Utils      - Email templates & sending logic          │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MODEL LAYER (ORM)                        │
├─────────────────────────────────────────────────────────────────┤
│  SQLAlchemy Models (app/models/)                                 │
│  ├─ Workshop             - Workshops with objectives             │
│  ├─ Participant          - Workshop participants                 │
│  ├─ Session              - Workshop sessions                     │
│  ├─ ObservationalRecord  - Therapeutic observations (JSON)       │
│  ├─ User                 - System users with auth methods        │
│  ├─ Role                 - User roles (Admin, Editor)            │
│  ├─ UserInvitation       - Invitation tokens                     │
│  └─ observation_questions.py - Question structure (config)       │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Database                                                        │
│  ├─ Development:  SQLite (arteterapia.db)                       │
│  └─ Production:   PostgreSQL / MySQL (via SQLAlchemy)           │
│                                                                  │
│  Migrations: Flask-Migrate (Alembic)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Model Relationships

```
┌──────────────────────┐
│       User           │
│ ─────────────────   │
│ • id                │
│ • username          │◄─────────┐
│ • email             │          │
│ • password_hash     │          │ Many-to-Many
│ • email_verified    │          │
└──────┬───────────────┘          │
       │                          │
       │ One-to-Many         ┌────┴──────────┐
       │                     │     Role      │
       ▼                     │ ───────────── │
┌─────────────────────┐      │ • id          │
│  UserInvitation     │      │ • name        │
│ ─────────────────   │      │ • description │
│ • id                │      └───────────────┘
│ • email             │
│ • token             │      ┌──────────────────────┐
│ • created_by        │      │     Workshop         │
│ • expires_at        │      │ ──────────────────── │
└─────────────────────┘      │ • id                 │
                             │ • name               │
                             │ • objective          │
                             │ • schedule           │
                             └───┬──────────────┬───┘
                                 │              │
                    ┌────────────┘              └───────────────┐
                    │ One-to-Many                   One-to-Many │
                    ▼                                           ▼
        ┌─────────────────────┐                   ┌──────────────────────┐
        │    Session          │                   │    Participant       │
        │ ─────────────────   │                   │ ──────────────────── │
        │ • id                │                   │ • id                 │
        │ • workshop_id       │                   │ • workshop_id        │
        │ • name              │                   │ • name               │
        │ • prompt            │                   │ • age                │
        │ • motivation        │                   │ • additional_info    │
        │ • materials         │                   └────────┬─────────────┘
        │ • scheduled_date    │                            │
        └────────┬────────────┘                            │
                 │                                          │
                 │ Many-to-One                              │ Many-to-One
                 │                                          │
                 └──────────────────┬───────────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   ObservationalRecord        │
                     │ ──────────────────────────── │
                     │ • id                         │
                     │ • session_id                 │
                     │ • participant_id             │
                     │ • workshop_id                │
                     │ • answers (JSON)             │
                     │ • notes (TEXT)               │
                     │ • created_at                 │
                     └──────────────────────────────┘
```

---

## Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEW USER REGISTRATION                        │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────┐
    │  Admin   │
    └────┬─────┘
         │
         ├─► 1. Creates invitation via /auth/create-invitation
         │
    ┌────▼───────────────────┐
    │  UserInvitation        │
    │  • token generated     │
    │  • expires in 7 days   │
    └────┬───────────────────┘
         │
         ├─► 2. Email sent with registration link
         │
    ┌────▼────────┐
    │  New User   │
    └────┬────────┘
         │
         ├─► 3. Clicks link, registers at /auth/register/<token>
         │
    ┌────▼──────────────┐
    │  User created      │
    │  • password hashed │
    │  • email_verified=False
    └────┬───────────────┘
         │
         ├─► 4. Verification email sent
         │
         ├─► 5. User verifies email via link
         │
    ┌────▼──────────────┐
    │  email_verified=True
    └────┬───────────────┘
         │
         └─► 6. User can now log in


┌─────────────────────────────────────────────────────────────────┐
│                         LOGIN FLOW                               │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────┐
    │   User   │
    └────┬─────┘
         │
         ├─► 1. Submits credentials to /auth/login
         │
    ┌────▼─────────────────┐
    │  User.check_password │
    │  (verify hash)       │
    └────┬─────────────────┘
         │
         ├─► 2. If valid: Flask-Login creates session
         │
    ┌────▼────────────────┐
    │  current_user       │
    │  is_authenticated   │
    └────┬────────────────┘
         │
         ├─► 3. Redirect to workshop list
         │
         └─► 4. Session maintained via cookies


┌─────────────────────────────────────────────────────────────────┐
│                    ROUTE PROTECTION                              │
└─────────────────────────────────────────────────────────────────┘

    Request to protected route
              │
              ▼
    ┌─────────────────────┐
    │  @login_required    │◄────── All routes except /auth/*
    └──────────┬──────────┘
               │
               ├─ Not authenticated ──► Redirect to /auth/login
               │
               └─ Authenticated
                       │
                       ▼
           ┌───────────────────────┐
           │ Check route requires  │
           │      admin role?      │
           └──────┬────────────────┘
                  │
                  ├─ Yes ──► current_user.is_admin()?
                  │              │
                  │              ├─ Yes ──► Allow access
                  │              └─ No ──► Redirect to home + flash error
                  │
                  └─ No ──► Allow access
```

---

## Observation Recording Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  OBSERVATION STEP-BY-STEP                        │
└─────────────────────────────────────────────────────────────────┘

Workshop Detail Page
      │
      ├─► Session expanded
      │
      ├─► User clicks participant name
      │
      ▼
┌──────────────────────────┐
│ /session/<id>/observe/   │
│   <participant_id>       │
└──────────┬───────────────┘
           │
           ├─► Load observation_questions.py
           │
           ├─► Get all questions (~50) in order
           │
           ├─► Display question 1 of ~50
           │
           ▼
    ┌────────────────┐
    │  Question X    │  ◄──┐
    │  [Category]    │     │
    │  [Subcategory] │     │
    └────────┬───────┘     │
             │              │
             ├─► User selects answer (Yes/No/Not Sure/Not Applicable)
             │              │
             ├─► AJAX POST answer to server
             │              │
             ├─► Server stores in session or DB
             │              │
             ├─► Next question ──┘
             │
             └─► Question ~50 reached
                     │
                     ▼
          ┌─────────────────────┐
          │  Optional Notes     │
          │  (freeform text)    │
          └──────────┬──────────┘
                     │
                     ├─► User submits
                     │
                     ▼
          ┌──────────────────────────┐
          │  ObservationalRecord     │
          │  • answers: JSON         │
          │  • notes: TEXT           │
          │  • session_id            │
          │  • participant_id        │
          └──────────┬───────────────┘
                     │
                     └─► Redirect to workshop detail
                     
                     
┌─────────────────────────────────────────────────────────────────┐
│              CONSOLIDATED OBSERVATION VIEW                       │
└─────────────────────────────────────────────────────────────────┘

Workshop Detail Page
      │
      ├─► User clicks "Ver registros" (View records)
      │
      ▼
┌────────────────────────┐
│ /workshop/<id>/        │
│  observations          │
└──────────┬─────────────┘
           │
           ├─► Load all ObservationalRecords for workshop
           │
           ├─► Group by category from observation_questions.py
           │
           ▼
    ┌──────────────────────────────────────────┐
    │          TABLE VIEW                      │
    ├──────────────────────────────────────────┤
    │ Session | Participant | Category | Q1... │
    ├──────────────────────────────────────────┤
    │ Sesión 1│ María       │ Entry    │ Yes...│
    │         │             │ Motivation│ No...│
    │         │             │ ...      │ ...   │
    ├──────────────────────────────────────────┤
    │ Sesión 1│ Juan        │ Entry    │ Yes...│
    │         │             │ ...      │ ...   │
    └──────────────────────────────────────────┘
```

---

## Request/Response Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│              HTTP REQUEST/RESPONSE FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Browser Request (e.g., GET /workshop/1)
           │
           ▼
    ┌──────────────┐
    │ Flask Router │
    └──────┬───────┘
           │
           ├─► Match route to blueprint
           │
           ▼
    ┌─────────────────────┐
    │  Blueprint Handler  │  (e.g., workshop_bp.detail)
    └──────┬──────────────┘
           │
           ├─► @login_required check
           │       │
           │       ├─ Not authenticated ──► Redirect to /auth/login
           │       │
           │       └─ Authenticated ──► Continue
           │
           ├─► Check permissions if needed (e.g., is_admin())
           │
           ├─► Query database via SQLAlchemy
           │
           ▼
    ┌──────────────┐
    │  db.session  │
    └──────┬───────┘
           │
           ├─► Execute query
           │
           └─► Return model objects
                   │
                   ▼
    ┌─────────────────────────┐
    │   render_template()     │
    └──────┬──────────────────┘
           │
           ├─► Jinja2 template engine
           │
           ├─► Render HTML
           │
           ▼
    ┌──────────────┐
    │  HTML Response│ ──► Browser displays page
    └───────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    AJAX REQUEST FLOW                             │
└─────────────────────────────────────────────────────────────────┘

JavaScript: fetch('/workshop/1/update-objective', {method: 'POST'})
           │
           ▼
    ┌──────────────┐
    │ Flask Router │
    └──────┬───────┘
           │
           ├─► Route handler
           │
           ├─► Parse JSON body
           │
           ├─► Validate data
           │
           ├─► Update database
           │
           ▼
    ┌──────────────────────┐
    │  jsonify(response)   │ ──► {'success': True, 'data': {...}}
    └──────┬───────────────┘
           │
           └─► Browser receives JSON
                   │
                   ├─► Update UI dynamically
                   │
                   └─► No page reload
```

---

## File Organization Rationale

```
app/
├── __init__.py           ─► Factory pattern, extension init, blueprint registration
├── admin_views.py        ─► Centralized admin customization (security, formatting)
│
├── routes/               ─► Domain-based route organization
│   ├── auth.py           ─► All authentication routes together
│   ├── workshop.py       ─► All workshop routes together
│   └── ...               ─► Separation of concerns
│
├── models/               ─► Data layer, one file per entity
│   ├── workshop.py       ─► Self-contained model with relationships
│   ├── observation_questions.py  ─► Configuration, not a DB model
│   └── ...
│
├── templates/            ─► Organized by feature
│   ├── base.html         ─► DRY principle - single layout
│   ├── auth/             ─► All auth templates grouped
│   └── workshop/         ─► All workshop templates grouped
│
└── static/               ─► Public assets
    ├── css/custom.css    ─► Single source of truth for styles
    └── js/app.js         ─► Vanilla JS, no build process needed
```

**Rationale:**
- **Blueprints**: Modular, testable, clean separation
- **Single CSS file**: Avoid fragmentation, easier maintenance
- **Template inheritance**: base.html prevents duplication
- **Model/Controller separation**: Easier to reason about data vs. business logic

---

*For implementation details, see [AGENT_GUIDELINES.md](AGENT_GUIDELINES.md).*
