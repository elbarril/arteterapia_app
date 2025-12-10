---
description: Add or Modify Database Models
---

# Add or Modify Database Models

This workflow guides you through making changes to database models safely.

## Steps

### 1. Identify the Change Needed
Clearly define what model changes are required:
- New model/table?
- New column?
- Modify existing column?
- New relationship?
- Foreign key constraint?

### 2. Edit Model File
Navigate to `app/models/` and edit the appropriate model file:
- `workshop.py` - Workshop model
- `participant.py` - Participant model
- `session.py` - Session model
- `observation.py` - ObservationalRecord model
- `user.py` - User model
- `role.py` - Role model
- `user_invitation.py` - UserInvitation model

Or create a new model file if adding a new entity.

### 3. Update Model Imports
If creating a new model, add import to `app/models/__init__.py`:
```python
from app.models.your_new_model import YourNewModel
```

Also add to `app/__init__.py` in the create_app function (import section).

### 4. Stop Running Flask Application
**IMPORTANT:** Stop the Flask dev server if it's running:
```
Press Ctrl+C in the terminal
```

### 5. Create Migration
```bash
flask --app run db migrate -m "Descriptive message about change"
```

Example messages:
- "Add email column to Participant model"
- "Create new MaterialsUsed model"
- "Add cascade delete to Session-Observation relationship"

### 6. Review Migration File
Check the generated migration in `migrations/versions/`:
- Verify upgrade() function is correct
- Verify downgrade() function is correct
- Check for any missing imports or type definitions

### 7. Apply Migration
```bash
flask --app run db upgrade
```

### 8. Verify Database Schema
Optional - inspect database:
```bash
sqlite3 arteterapia.db
.schema your_table_name
.exit
```

### 9. Update Admin Views (if needed)
If adding/modifying models that should appear in Flask-Admin:
- Edit `app/admin_views.py`
- Add/modify ModelView for the entity
- Register in `app/__init__.py`

### 10. Restart Flask Application
```bash
python run.py
```

### 11. Test Changes
- Verify application starts without errors
- Test CRUD operations on modified models
- Check Flask-Admin panel
- Verify relationships work correctly

## Important Notes

### Avoiding Data Loss
- **Never drop columns** with existing data in production without backup
- Test migrations on development database first
- Use `db upgrade` and `db downgrade` to test reversibility

### Complex Migrations
For data transformations, edit migration file manually:
```python
def upgrade():
    # Add new column with default
    op.add_column('table_name', sa.Column('new_col', sa.String(100), nullable=True))
    
    # Populate data
    connection = op.get_bind()
    connection.execute("UPDATE table_name SET new_col='default_value'")
    
    # Make non-nullable if needed
    op.alter_column('table_name', 'new_col', nullable=False)
```

### Foreign Keys in SQLite
SQLite requires special handling for foreign key changes. Consider recreating the table if modifying foreign keys.

## Troubleshooting

**Migration fails with "Table already exists":**
- Check if migration was partially applied
- Consider rolling back: `flask --app run db downgrade`
- Or fix manually and mark as applied

**Database locked error:**
- Stop all Flask instances
- Close any SQLite browser tools
- Try again

**Column doesn't appear after migration:**
- Verify migration was applied (check migrations/versions/ folder)
- Check database schema directly
- Restart Flask application
