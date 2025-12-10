---
description: Reset Database for Testing
---

# Reset Database for Testing

This workflow resets the database to a clean state, optionally with sample data.

⚠️ **WARNING: This deletes ALL existing data. Only use in development!**

## When to Use This Workflow
- Need to test with fresh data
- Database schema is corrupted
- Want to repopulate sample data
- Testing user registration flow from scratch
- Development database has become cluttered

## Steps

### 1. Stop Flask Application
**CRITICAL:** Stop the running Flask dev server:
```
Press Ctrl+C in terminal where Flask is running
```

If you don't stop Flask, you'll get a "database is locked" error.

### 2. Choose Reset Option

**Option A: Reset with Sample Data (Recommended for Development)**
```bash
python setup_db.py --reset --with-data
```

This will:
- Drop all tables
- Recreate schema
- Create admin user (admin/admin123)
- Create editor role
- Populate 3 workshops with participants, sessions, and observations

**Option B: Reset Database (Admin Only)**
```bash
python setup_db.py --reset
```

This will:
- Drop all tables
- Recreate schema
- Create admin user (admin/admin123)
- Create editor role
- No sample data

### 3. Verify Database Reset
Check console output for:
```
Database reset successful!
Tables dropped and recreated.
Admin user created: admin / admin123
[Optional] Sample data created successfully!
```

### 4. Restart Flask Application
```bash
python run.py
```

### 5. Verify Application
- Navigate to http://localhost:5000
- Log in with `admin` / `admin123`
- Verify data state:
  - **With sample data**: Should see 3 workshops
  - **Without sample data**: Should see empty workshop list

## Sample Data Details

When using `--with-data`, the following is created:

### Workshops (3)
1. **Taller de Exploración Creativa** - Scheduled Mondays 10:00-12:00
2. **Taller de Identidad y Expresión** - Scheduled Wednesdays 15:00-17:00
3. **Taller de Arte y Naturaleza** - Scheduled Fridays 9:00-11:00

### Participants (2 per workshop, 6 total)
- María García, Juan Pérez (Workshop 1)
- Ana Martínez, Carlos López (Workshop 2)
- Laura Rodríguez, Pedro Sánchez (Workshop 3)

### Sessions (2 per workshop, 6 total)
Each session has:
- Prompt (consigna)
- Motivation
- Materials list
- Status (scheduled/completed)

### Observational Records (1-2 per workshop)
- Sample observations with answers to questions
- Therapist notes included
- Demonstrates complete observation flow

## Important Notes

### Production Warning
**NEVER run `--reset` in production!**
- This is destructive and permanent
- All user data will be lost
- No backup is created automatically

### Data Backup (Production)
Before resetting in production (if absolutely necessary):
```bash
# SQLite
cp arteterapia.db arteterapia_backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL
pg_dump -U username database_name > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Default Admin Credentials
After reset:
- **Username**: `admin`
- **Password**: `admin123`
- **⚠️ Change immediately**: Navigate to `/auth/change-password`

## Troubleshooting

**Database is locked error:**
- Stop ALL Flask instances
- Close any database browser tools (DB Browser for SQLite, etc.)
- Wait 5 seconds
- Try again

**Migration conflict after reset:**
If you get migration version errors:
```bash
# This shouldn't happen with --reset, but if it does:
flask --app run db stamp head
```

**Sample data script fails:**
- Check console for specific error
- Ensure all model relationships are correct
- Verify foreign key constraints
- Try `--reset` without `--with-data` to isolate issue

**Cannot log in after reset:**
Verify admin user was created by checking console output. If not:
```bash
# Manually create admin via Python shell
flask --app run shell
>>> from app.models.user import User
>>> from app.models.role import Role
>>> from app import db
>>> admin_role = Role.query.filter_by(name='admin').first()
>>> user = User(username='admin', email='admin@example.com', email_verified=True)
>>> user.set_password('admin123')
>>> user.roles.append(admin_role)
>>> db.session.add(user)
>>> db.session.commit()
>>> exit()
```

## Quick Reference

**Stop Flask → Reset → Restart → Verify**

```bash
# Stop Flask (Ctrl+C)

# Reset with sample data
python setup_db.py --reset --with-data

# Restart Flask
python run.py
```
