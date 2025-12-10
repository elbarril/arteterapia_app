# Pre-Commit Hook Installation

This directory contains Git hooks for the Arteterapia project.

## Installing the Pre-Commit Hook

The pre-commit hook provides automated checks before each commit:
- Documentation reminders
- Sensitive file detection (.env, .db, .mo)
- Translation compilation reminders
- Database migration reminders
- Python syntax validation
- Trailing whitespace detection

### Windows (PowerShell)

```powershell
Copy-Item .hooks\pre-commit .git\hooks\pre-commit -Force
```

### macOS/Linux

```bash
cp .hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Git Bash on Windows

```bash
cp .hooks/pre-commit .git/hooks/pre-commit
```

## What the Hook Does

When you run `git commit`, the hook will:

1. **Remind you** about project documentation
2. **Block commits** containing:
   - `.env` files
   - Database files (`.db`, `.sqlite`)
   - Compiled translations (`.mo`)
   - `__pycache__` directories
3. **Remind you** to:
   - Compile translations if `.po` files changed
   - Create migrations if models changed
4. **Validate** Python syntax
5. **Warn** if modifying `observation_questions.py`

## Bypassing the Hook

If absolutely necessary (not recommended):

```bash
git commit --no-verify
```

## Uninstalling

```bash
# Windows PowerShell
Remove-Item .git\hooks\pre-commit

# macOS/Linux/Git Bash
rm .git/hooks/pre-commit
```

---

**Note:** Git hooks are not committed to the repository, so each developer needs to install them manually.
