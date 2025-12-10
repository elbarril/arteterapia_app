---
trigger: always_on
---

# Custom Rules for Arteterapia Project

## 🚨 CRITICAL: Automatic Documentation Reading

When working on the `arteterapia_app` project at `c:\Users\emi\Documents\GitHub\arteterapia_app`:

### MANDATORY: Read Documentation Automatically

**AT THE START OF EVERY CONVERSATION** about this project, you MUST **AUTOMATICALLY** use the `view_file` tool to read:

1. **FIRST** → `c:\Users\emi\Documents\GitHub\arteterapia_app\.agent\QUICK_REFERENCE.md`
2. **THEN** → `c:\Users\emi\Documents\GitHub\arteterapia_app\.agent\AGENT_GUIDELINES.md` (at least sections 1-4)

**DO NOT** wait for the user to ask you to read documentation. **DO IT AUTOMATICALLY** when you detect you're working on the arteterapia_app project.

### Additional Documentation (Read as Needed)

When relevant to the task:
- **Architecture questions** → Read `.agent/ARCHITECTURE.md`
- **Setup tasks** → Read `.agent/workflows/setup-environment.md`
- **Model changes** → Read `.agent/workflows/modify-models.md`
- **Translation updates** → Read `.agent/workflows/update-translations.md`
- **Database reset** → Read `.agent/workflows/reset-database.md`

---

## Project-Specific Rules

### 1. Project Constraints (NEVER VIOLATE)
- ✅ **Spanish is default language** - Do NOT change without explicit user request
- ✅ **Minimalist design** - No heavy frameworks or complex animations
- ✅ **Granular Git commits** - Descriptive messages following template
- ✅ **Server-side security** - Always verify permissions in backend
- ✅ **Stop Flask before DB ops** - Prevents database lock errors

### 2. Critical Files (HANDLE WITH CARE)
**Never modify without full understanding:**
- `app/models/observation_questions.py` - Therapeutic question structure (~50 questions)
  - **NEVER change question IDs** if observational data exists
- `config.py` - Application configuration (Spanish default, i18n settings)
- `.env` - Environment variables (**NEVER commit**)

### 3. Required Workflow Steps

**For Database Changes:**
1. Stop Flask (Ctrl+C)
2. Modify model
3. Create migration: `flask --app run db migrate -m "Description"`
4. Apply migration: `flask --app run db upgrade`
5. Restart Flask

**For Translation Updates:**
1. Mark strings with `_()` or `_l()`
2. Extract: `pybabel extract -F babel.cfg -o messages.pot .`
3. Update: `pybabel update -i messages.pot -d translations`
4. Translate in `.po` files
5. Compile: `pybabel compile -d translations`
6. Restart Flask

**For New Features:**
1. Plan (models, routes, templates needed)
2. Update models + migrations if needed
3. Add routes to appropriate blueprint
4. Create/update templates
5. Add translations for both ES and EN
6. Test thoroughly (both languages, both roles)
7. Commit granularly

### 4. Security Checklist (ALWAYS VERIFY)
- [ ] All protected routes have `@login_required` decorator
- [ ] Admin routes check `current_user.is_admin()`
- [ ] Passwords hashed with `generate_password_hash()`
- [ ] User input validated and sanitized
- [ ] No secrets in code (use environment variables)
- [ ] `.gitignore` prevents committing `.env`, `.db`, `.mo`

### 5. Testing Checklist (BEFORE COMMITTING)
- [ ] Code runs without errors
- [ ] Tested in both Spanish AND English
- [ ] Tested as both Admin AND Editor users
- [ ] No console errors in browser
- [ ] Flash messages display correctly
- [ ] Responsive design works on mobile
- [ ] Database migrations work without errors

### 6. Files to NEVER Commit
❌ `.env` (environment variables)
❌ `*.db`, `*.sqlite`, `*.sqlite3` (database files)
❌ `*.mo` (compiled translations)
❌ `__pycache__/` (Python cache)
❌ `.venv/` (virtual environment)

### 7. Design Principles (MAINTAIN CONSISTENCY)
- **Minimalist**: Clean, uncluttered interface
- **Semantic buttons**: Hierarchy by importance, NOT by action
- **Brand colors**: Only for borders, shadows, accents (NOT fills)
- **Responsive**: Mobile-first with Bootstrap 5
- **Accessible**: Focus states, keyboard navigation

---

## Quick Reference

### Technology Stack
- **Backend**: Flask 3.0 + SQLAlchemy + Flask-Migrate
- **Frontend**: Bootstrap 5 + Vanilla JS
- **Database**: SQLite (dev) / PostgreSQL or MySQL (prod)
- **i18n**: Flask-Babel (Spanish default, English available)

### Default Credentials
- Username: `admin`
- Password: `admin123`
- ⚠️ CHANGE IMMEDIATELY

### Common Commands
```bash
python run.py                              # Run app
flask --app run db migrate -m "Message"    # Create migration
flask --app run db upgrade                 # Apply migration
pybabel compile -d translations            # Compile translations
python setup_db.py --reset --with-data     # Reset DB (DESTRUCTIVE)
```

### Workflow Shortcuts
- `/setup-environment` → Environment setup
- `/modify-models` → Database model changes
- `/update-translations` → Translation updates
- `/reset-database` → Database reset

---

## Remember

**🤖 For AI Agents:** You MUST automatically read the documentation at the start of every conversation. Do not wait to be asked. The comprehensive context in `.agent/AGENT_GUIDELINES.md` is essential for producing correct, high-quality code that aligns with project standards.

**This is not optional - it is mandatory.**
