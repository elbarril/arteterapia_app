# Project Quick Reference

## Project Identity
**Name:** Arteterapia  
**Type:** Flask Web Application  
**Purpose:** Art Therapy Workshop Management  
**Primary Language:** Spanish

---

## Technology Stack at a Glance

```
Backend:     Flask 3.0 + SQLAlchemy + Flask-Migrate
Admin:       Flask-Admin (role-protected)
Auth:        Flask-Login (invitation-based registration)
Frontend:    Bootstrap 5 + Vanilla JS + Custom CSS
Database:    SQLite (dev) / PostgreSQL or MySQL (prod)
Email:       Flask-Mail
```

---

## Core Models (5 + 3 Auth)

### Application Models
1. **Workshop** - Art therapy workshops with objectives
2. **Participant** - Workshop participants
3. **Session** - Workshop sessions with prompts, materials
4. **ObservationalRecord** - Therapeutic observations with structured questions (JSON)
5. **ObservationQuestions** - Question structure (not a model, config file)

### Authentication Models
6. **User** - System users with password authentication
7. **Role** - User roles (Admin, Editor)
8. **UserInvitation** - Invitation tokens for registration

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `run.py` | Application entry point |
| `config.py` | All configuration (Dev/Prod) |
| `app/__init__.py` | Flask factory, blueprints, extensions |
| `app/models/observation_questions.py` | **CRITICAL** - Therapeutic question structure (~50 questions) |
| `app/static/css/custom.css` | Minimalist design system |
| `setup_db.py` | Database initialization script |

---

## Routes Map

### Public
- `/auth/login` - Login page
- `/auth/register/<token>` - Registration (invitation-based)

### Protected (login required)
- `/` - Workshop list
- `/workshop/<id>` - Workshop detail
- `/session/<id>/observe/<participant_id>` - Record observations

### Admin Only
- `/admin` - Flask-Admin panel
- `/auth/create-invitation` - Create user invitations

---

## Default Credentials

```
Username: admin
Password: admin123
⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN
```

---

## Essential Commands

### Setup
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python setup_db.py --with-data
python run.py
```

### Database
```bash
python setup_db.py --reset --with-data    # Reset with sample data
flask --app run db migrate -m "Message"   # Create migration
flask --app run db upgrade                # Apply migration
```

---

## Design Principles

### UI/UX
✅ **Minimalist** - Clean, uncluttered interface  
✅ **Semantic** - Button hierarchy based on importance, not action  
✅ **Brand Colors** - Applied to borders, shadows, accents (not fills)  
✅ **Responsive** - Mobile-first with Bootstrap 5  
✅ **Accessible** - Focus states, keyboard navigation  

### Code
✅ **Application Factory** - Modular Flask app creation  
✅ **Blueprints** - Organized route handlers by domain  
✅ **Role-Based Access** - Admin vs Editor permissions  
✅ **SQLAlchemy ORM** - Database abstraction, migration-ready  

---

## Observation System

### 8 Question Categories (~50 questions total)

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
Answers stored as JSON in `ObservationalRecord.answers` field:
```json
{
  "entry_on_time": "yes",
  "entry_resistance": "no",
  "motivation_interest": "yes",
  ...
}
```

---

## Security Checklist

- [ ] `SECRET_KEY` is 64-character random hex
- [ ] `.env` is never committed (in `.gitignore`)
- [ ] Default admin password changed on first login
- [ ] All protected routes use `@login_required`
- [ ] Admin routes check `current_user.is_admin()`
- [ ] Passwords hashed with Werkzeug
- [ ] Email verification required for new users
- [ ] Tokens expire (password reset: 24h, invitations: 7d)

---

## Common Pitfalls

❌ **Don't:** Modify question IDs in `observation_questions.py` if data exists  
❌ **Don't:** Commit `.env`, `.db`, `.mo` files  
❌ **Don't:** Run `--reset` in production without backup  
❌ **Don't:** Hardcode action colors (use semantic hierarchy)  
❌ **Don't:** Skip `@login_required` on protected routes  

✅ **Do:** Create migrations after model changes  
✅ **Do:** Stop Flask before database reset  
✅ **Do:** Follow minimalist design principles  

---

## File Size Reference

| Category | Files |
|----------|-------|
| Configuration | `config.py`, `.env`, `.env.example`, `babel.cfg` |
| Entry Points | `run.py`, `setup_db.py` |
| Models | 9 files in `app/models/` |
| Routes | 6 blueprints in `app/routes/` |
| Templates | ~10 files across `auth/`, `workshop/`, `observation/` |
| Static | `custom.css` (~330 lines), `app.js` |
| Admin | `admin_views.py` (7 custom views) |

---

## Development Workflow Summary

1. **Plan** - Identify required changes
2. **Models** - Update/create models if needed
3. **Migrate** - Create and apply migrations
4. **Routes** - Add/modify route handlers
5. **Templates** - Update Jinja2 templates
6. **Test** - Manual browser testing
7. **Commit** - Granular, descriptive commits

---

## Support Resources

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Bootstrap 5: https://getbootstrap.com/
- Flask-Admin: https://flask-admin.readthedocs.io/

---

*This is a quick reference. For comprehensive documentation, see [AGENT_GUIDELINES.md](AGENT_GUIDELINES.md).*
