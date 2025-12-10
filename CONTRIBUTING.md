# Contributing to Arteterapia

Thank you for contributing to the Arteterapia project!

---

## 🤖 **MANDATORY: Read Documentation First**

**Before making ANY contribution** (code, documentation, or fixes), you **MUST** read:

### 📘 Primary Documentation
1. **[`.agent/AGENT_GUIDELINES.md`](.agent/AGENT_GUIDELINES.md)** - Complete project guide
   - Architecture and technology stack
   - Database models and relationships
   - Authentication system
   - Security guidelines
   - Development standards

### 📊 Architecture & Reference
2. **[`.agent/ARCHITECTURE.md`](.agent/ARCHITECTURE.md)** - Visual system diagrams
3. **[`.agent/QUICK_REFERENCE.md`](.agent/QUICK_REFERENCE.md)** - Fast lookup reference

### 📂 Task-Specific Workflows
4. **[`.agent/workflows/`](.agent/workflows/)** - Step-by-step guides
   - `setup-environment.md` - Environment setup
   - `reset-database.md` - Database reset

**Estimated reading time:** 20-30 minutes for complete context

---

## 🎯 Contribution Guidelines

### Code Contributions

#### Before Starting
- [ ] Read `.agent/AGENT_GUIDELINES.md` completely
- [ ] Review relevant workflow in `.agent/workflows/`
- [ ] Understand the project architecture
- [ ] Check existing issues and pull requests

#### Development Standards

**Code Style:**
- Follow PEP 8 for Python code
- Use snake_case for functions/variables
- Use PascalCase for classes
- Add docstrings to all classes and non-trivial functions

**Git Workflow:**
- Create a descriptive branch name: `feature/name` or `fix/name`
- Make granular, focused commits
- Write clear commit messages (see template below)
- Reference issues in commits when applicable

**Testing:**
- Test all changes manually in browser
- Test both  Admin and Editor user perspectives

#### Commit Message Format

Use the provided Git commit template (`.gitmessage`):

```
<type>: <subject>

<body (optional)>

# Type: feat, fix, docs, refactor, test, chore, i18n, db
# 
# Examples:
# feat: Add participant filtering by age
# fix: Resolve language switcher session bug
# db: Add cascade delete to Session-Observation
# i18n: Update English translations for auth module
```

**Committing Guidelines:**
- **Descriptive Messages**: Always include a clear and descriptive message explaining *what* changed and *why*.
- **Granular Commits**: If you have multiple distinct changes (e.g., a documentation update and a code fix), try to commit them separately with appropriate types.
- **Verification**: Ensure you have tested your changes before committing.

Use the provided Git commit template (`.gitmessage`):

```
<type>: <subject>

<body (optional)>

# Type: feat, fix, docs, refactor, test, chore, i18n, db
# 
# Examples:
# feat: Add participant filtering by age
# fix: Resolve language switcher session bug
# db: Add cascade delete to Session-Observation
# i18n: Update English translations for auth module
```

---

## 🔒 Security Guidelines

**NEVER commit:**
- `.env` files (use `.env.example` as template)
- Database files (`.db`, `.sqlite`)
- Compiled translations (`.mo` files)
- `__pycache__/` directories
- Virtual environment directories

**Always:**
- Use `@login_required` on protected routes
- Verify admin role with `current_user.is_admin()` for admin features
- Hash passwords using `generate_password_hash()`
- Validate and sanitize user input
- Use parameterized queries (SQLAlchemy handles this)

---

## 🗄️ Database Changes

**When modifying models:**

1. Edit model in `app/models/`
2. Stop Flask application (Ctrl+C)
3. Create migration: `flask --app run db migrate -m "Description"`
4. Review migration file in `migrations/versions/`
5. Apply migration: `flask --app run db upgrade`
6. Restart Flask application
7. Test changes thoroughly

⚠️ **CRITICAL:** Never modify question IDs in `app/models/observation_questions.py` if observational data exists!

See [`.agent/workflows/modify-models.md`](.agent/workflows/modify-models.md) for details.

---

## 🎨 Design Principles

### UI/UX Standards
- **Minimalist**: Clean, uncluttered interface
- **Semantic buttons**: Hierarchy based on importance, not action
- **Brand colors**: Only for borders, shadows, and accents (not fills)
- **Responsive**: Mobile-first with Bootstrap 5
- **Accessible**: Focus states, keyboard navigation, proper contrast

### CSS Guidelines
- Use CSS variables defined in `:root` of `app/static/css/custom.css`
- Follow existing naming conventions
- Maintain semantic class names
- Test responsiveness at multiple breakpoints
- Verify accessibility (WCAG 2.1 AA)

---

## 🧪 Testing Checklist

Before submitting a contribution:

- [ ] Code runs without errors
- [ ] Tested as both Admin and Editor users
- [ ] No console errors in browser
- [ ] Database migrations work correctly
- [ ] Flash messages display properly
- [ ] Responsive design works on mobile
- [ ] Changes align with project documentation
- [ ] `.gitignore` prevents committing sensitive files

---

## 📝 Pull Request Process

1. **Update Documentation**
   - Update `.agent/AGENT_GUIDELINES.md` if architecture changes
   - Update workflows if process changes
   - Update `README.md` if user-facing changes
   - Add to `CHANGELOG.md` if it exists

2. **Create Pull Request**
   - Clear title describing the change
   - Reference related issues
   - List changes made
   - Include testing steps
   - Note any breaking changes

3. **Code Review**
   - Address review feedback promptly
   - Keep discussions focused and professional
   - Update documentation based on feedback

---

## 🚫 What NOT to Do

❌ **Don't** modify without reading documentation first  
❌ **Don't** change the default language from Spanish  
❌ **Don't** modify observation question IDs  
❌ **Don't** commit `.env`, `.db`, or `.mo` files  
❌ **Don't** run `--reset` commands in production  
❌ **Don't** skip security best practices  

---

## ✅ Best Practices

✅ **Do** read `.agent/AGENT_GUIDELINES.md` first  
✅ **Do** use workflows for common tasks  
✅ **Do** write descriptive commit messages  
✅ **Do** follow established patterns  
✅ **Do** ask questions if unsure  
✅ **Do** update documentation when needed  

---

## 🆘 Getting Help

### Documentation Resources
- **Comprehensive Guide**: `.agent/AGENT_GUIDELINES.md`
- **Quick Reference**: `.agent/QUICK_REFERENCE.md`
- **Architecture**: `.agent/ARCHITECTURE.md`
- **Workflows**: `.agent/workflows/`

### External Resources
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Bootstrap 5: https://getbootstrap.com/

---

## 📋 Quick Command Reference

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python setup_db.py --with-data

# Development
python run.py

# Database
flask --app run db migrate -m "Message"
flask --app run db upgrade
python setup_db.py --reset --with-data  # DESTRUCTIVE
```

---

## 🎓 For AI Agents

If you're an AI agent working on this project:

1. **Read** `.agent/AGENT_GUIDELINES.md` before ANY code generation
2. **Reference** `.agent/QUICK_REFERENCE.md` for quick lookups
3. **Use** workflows in `.agent/workflows/` for common tasks
4. **Verify** security implications of all changes
6. **Follow** minimalist design principles

The comprehensive documentation ensures you have complete context for high-quality contributions.

---

**Thank you for contributing and maintaining high standards!** 🎨✨
