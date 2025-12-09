# Arteterapia - Workshop Management Application

A complete Flask-based web application for art therapists to manage workshops, sessions, participants, and therapeutic observational records.

## Features

- **Workshop Management**: Create and manage art therapy workshops with objectives
- **Participant Tracking**: Add and manage participants for each workshop
- **Session Planning**: Define sessions with prompts, motivations, and materials
- **Observational Records**: Step-by-step therapeutic observation flow with 8 comprehensive categories
- **Consolidated Reporting**: View all observations in a structured table format
- **Admin Interface**: Full CRUD operations for internal testing and data correction
- **Internationalization**: Built-in i18n support (Spanish default, English available)
- **Database Portability**: SQLAlchemy + Alembic for easy database migration

## Technology Stack

- **Backend**: Flask 3.0
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL or MySQL ready
- **Migrations**: Flask-Migrate (Alembic)
- **Admin**: Flask-Admin
- **i18n**: Flask-Babel
- **Frontend**: Bootstrap 5 + Custom minimalist CSS
- **JavaScript**: Vanilla JS with AJAX for dynamic interactions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone or download the repository**

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Setup the database**:
   
   **Option A: With sample data (recommended for testing)**
   ```bash
   python setup_db.py --with-data
   ```
   
   **Option B: Admin user only (for production)**
   ```bash
   python setup_db.py
   ```
   
   This will:
   - Create all database tables
   - Set up admin and editor roles
   - Create admin user (username: `admin`, password: `admin123`)
   - Optionally populate with realistic sample data

6. **Run the application**:
   ```bash
   python run.py
   ```

7. **Access the application**:
   - Main application: http://localhost:5000
   - Admin interface: http://localhost:5000/admin
   - Login with: `admin` / `admin123` (change password on first login!)

### Database Setup Options

See `DATABASE_SETUP.md` for detailed documentation on:
- Resetting the database
- Sample data details
- Troubleshooting
- Advanced options

**Quick Reference:**
```bash
# Setup with sample data
python setup_db.py --with-data

# Reset database with sample data
python setup_db.py --reset --with-data

# Reset database (admin only)
python setup_db.py --reset
```

⚠️ **Important:** Stop the Flask application (`Ctrl+C`) before running `--reset` commands!

## Environment Configuration

### Setting Up Environment Variables

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Configure required variables** in `.env`:

   ```bash
   # Flask Configuration
   SECRET_KEY=your-secret-key-here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
   FLASK_ENV=development
   
   # Database (SQLite by default, can use PostgreSQL/MySQL)
   DATABASE_URL=sqlite:///arteterapia.db
   
   # Email Configuration (for user invitations and password resets)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   
   # Admin Configuration
   ADMIN_EMAIL=admin@example.com
   ```

3. **Email Setup Notes**:
   - For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password
   - In development, emails are printed to console if `FLASK_ENV=development`
   - For production, configure a proper SMTP server

## Authentication System

### User Roles and Permissions

The application uses role-based access control with two roles:

- **Admin**: Full access to application, can create invitations, access Flask-Admin panel
- **Editor**: Can manage workshops, participants, sessions, and observations

### User Registration Flow

**Invitation-Based Registration** (Admin only):

1. Admin logs in and navigates to create invitation endpoint
2. Admin generates invitation link with email
3. New user receives email with registration link
4. User registers with the invitation token
5. User verifies email (link sent automatically)
6. User can now log in and access the application

**Manual Invitation Creation**:
```bash
# Visit the create invitation endpoint (admin only)
http://localhost:5000/auth/create-invitation
```

### Login and Password Management

**First Login**:
```
URL: http://localhost:5000/auth/login
Default Admin: admin / admin123
```

⚠️ **Change the default admin password immediately after first login!**

**Password Reset Flow**:
1. Click "Forgot Password" on login page
2. Enter registered email address
3. Receive password reset link via email
4. Click link and set new password
5. Log in with new credentials

**Changing Password** (when logged in):
- Navigate to: http://localhost:5000/auth/change-password
- Enter current password and new password
- Confirm changes

### Protected Routes

All workshop, participant, session, and observation routes require authentication:
- Users must be logged in to access any CRUD operations
- Admin routes (`/admin/*`) require admin role
- Unauthenticated users are redirected to login page

## Security Considerations

### Best Practices

1. **Secret Key**: Always generate a strong, random secret key for production
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Password Policy**:
   - Minimum 6 characters (configurable in code)
   - Passwords are hashed using Werkzeug's security utilities
   - Never store plain-text passwords

3. **Email Verification**: Users must verify their email before accessing the application

4. **Token Expiration**:
   - Password reset tokens expire after 1 hour
   - Email verification tokens expire after 24 hours

5. **Environment Variables**: Never commit `.env` file to version control (already in `.gitignore`)

6. **Database Security**:
   - Use environment variables for database credentials
   - For production, use PostgreSQL or MySQL instead of SQLite
   - Regular backups recommended

7. **HTTPS in Production**: Always use HTTPS for production deployments to protect user credentials

### Production Deployment Checklist

- [ ] Generate new `SECRET_KEY`
- [ ] Change default admin password
- [ ] Configure production database (PostgreSQL/MySQL)
- [ ] Set up proper email server (not Gmail)
- [ ] Enable HTTPS/SSL
- [ ] Set `FLASK_ENV=production`
- [ ] Configure firewall and security groups
- [ ] Set up regular database backups
- [ ] Review and restrict admin access


## Project Structure

```
arteterapia_app/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── models/               # Data models
│   │   ├── workshop.py       # Workshop entity
│   │   ├── participant.py    # Participant entity
│   │   ├── session.py        # Session entity
│   │   ├── observation.py    # Observational record entity
│   │   └── observation_questions.py  # Therapeutic questions
│   ├── controllers/          # Route handlers and business logic
│   │   ├── workshop.py
│   │   ├── participant.py
│   │   ├── session.py
│   │   └── observation.py
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html
│   │   ├── workshop/
│   │   └── observation/
│   └── static/
│       ├── css/
│       │   └── custom.css    # Minimalist design
│       └── js/
│           └── app.js        # AJAX interactions
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
└── run.py                    # Application entry point
```

## Usage Guide

### Creating a Workshop

1. Click the "+" button on the main screen
2. Enter the workshop name
3. Click "Crear" to create

### Managing Workshop Details

From the workshop detail view, you can:

- **Edit Objective**: Click on the objective area to edit inline
- **Add Participants**: Click the "+" button in the Participants section
- **Add Sessions**: Click the "+" button in the Sessions section
- **Expand Sessions**: Click on a session header to view details

### Recording Observations

1. Navigate to a workshop
2. Expand a session
3. Click on a participant's name to start recording
4. Answer each question step-by-step
5. Add optional freeform notes at the end
6. Submit to save the record

### Viewing Consolidated Observations

From the workshop detail page, click "Ver registros" to view all observations in a table format with answers organized by category.

## Observational Categories

The application includes 8 comprehensive therapeutic observation categories:

1. **Entry into the Space**: Timeliness, resistance, greeting indicators
2. **Motivation**: Interest, rejection, repetition needs
3. **Instruction (Consigna)**: Concentration, comprehension, personal emergents
4. **Development**: Materials use, creativity, space interaction (with subcategories)
5. **Closure**: Creation acceptance, verbalization, associations
6. **Group**: Turn-taking, interaction, presence registration
7. **Group Climate**: Favorable, disruptive, indifferent, participatory

Each question has four answer options: Yes, No, Not Sure, Not Applicable.

## Database Migration

To switch from SQLite to PostgreSQL or MySQL:

1. Update the `DATABASE_URL` in `config.py` or set as environment variable
2. Install the appropriate database driver:
   - PostgreSQL: `pip install psycopg2-binary`
   - MySQL: `pip install mysqlclient`
3. Run migrations: `flask --app run db upgrade`

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development  # macOS/Linux
set FLASK_ENV=development     # Windows
python run.py
```

### Creating Database Migrations

After modifying models:

```bash
flask --app run db migrate -m "Description of changes"
flask --app run db upgrade
```

## Design Philosophy

- **Minimalist Design**: Clean interface with semantic button hierarchy
- **Brand Colors**: Applied to borders, icons, and shadows (not action-based)
- **Responsive**: Mobile-first design with Bootstrap 5
- **Accessible**: Focus states and keyboard navigation
- **Scalable**: Modular architecture for easy extension

## Admin Interface

Access the admin panel at `/admin` to:

- View and edit all workshops, participants, sessions, and observations
- Perform bulk operations
- Test data integrity
- Correct data errors

## License

This project is provided as-is for art therapy workshop management.

## Support

For issues or questions, refer to the Flask documentation:
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Bootstrap: https://getbootstrap.com/
