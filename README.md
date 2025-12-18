# Arteterapia - Workshop Management Application

A complete Flask-based web application for art therapists to manage workshops, sessions, participants, and therapeutic observational records.

---

## 🤖 For AI Agents & Developers

**IMPORTANT**: Before working on this project, read the comprehensive documentation in the **`.agent/`** directory:

- **[AGENT_GUIDELINES.md](.agent/AGENT_GUIDELINES.md)** - 📘 Complete project guide (READ THIS FIRST)
- **[QUICK_REFERENCE.md](.agent/QUICK_REFERENCE.md)** - ⚡ Fast lookup reference
- **[ARCHITECTURE.md](.agent/ARCHITECTURE.md)** - 📊 Visual system architecture
- **[Workflows](.agent/workflows/)** - 📂 Step-by-step task guides

**Workflow shortcuts**: `/setup-environment`, `/modify-models`, `/reset-database`

This documentation contains essential context including architecture, security guidelines, database models, observation question structure, and development standards.

---

## Features

### Core Functionality
- **Workshop Management**: Create and manage art therapy workshops with objectives
- **Participant Tracking**: Add and manage participants for each workshop
- **Session Planning**: Define sessions with prompts, motivations, and materials
- **Observational Records**: Step-by-step therapeutic observation flow with 8 comprehensive categories
- **Consolidated Reporting**: View all observations in a structured table format
- **Admin Interface**: Full CRUD operations for internal testing and data correction
- **Database Portability**: SQLAlchemy + Alembic for easy database migration

### Dual Architecture
- **Web Interface**: Traditional server-side rendered pages with Jinja2 templates
- **RESTful API**: JSON API with JWT authentication for external integrations
- **Frontend SPA**: Modern single-page application built with vanilla JavaScript
- **Service Layer**: Shared business logic between web and API endpoints
- **CORS Support**: Ready for frontend frameworks (React, Vue, Angular, mobile apps)

### Frontend SPA (New!)

A complete **vanilla JavaScript frontend** is now available in the `frontend/` directory:

- ✅ **Zero Dependencies**: Pure JavaScript, no frameworks required
- ✅ **JWT Authentication**: Secure login with automatic token refresh
- ✅ **Full CRUD**: Workshops and participants management
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Modern UI**: Toast notifications, modals, and smooth animations

**Quick Start:**
```bash
# Start the backend first
python run.py

# In a new terminal, start the frontend
cd frontend
python -m http.server 8000

# Open browser at http://localhost:8000/demo.html
```

See `frontend/README.md` for complete documentation.

## Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL or MySQL ready
- **Migrations**: Flask-Migrate (Alembic)
- **Admin**: Flask-Admin
- **API Auth**: Flask-JWT-Extended (JWT tokens)
- **CORS**: Flask-CORS

### Frontend
- **Templates**: Jinja2 with Bootstrap 5
- **Styling**: Custom minimalist CSS
- **JavaScript**: Vanilla JS with AJAX for dynamic interactions

### API
- **Format**: RESTful JSON API
- **Version**: v1 (`/api/v1/`)
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: See `.agent/docs/TESTING.md` for API testing guide

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
│   ├── routes/               # Route handlers (web interface)
│   │   ├── workshop.py
│   │   ├── participant.py
│   │   ├── session.py
│   │   └── observation.py
│   ├── api/                  # RESTful API endpoints
│   │   ├── __init__.py       # API blueprint (v1)
│   │   ├── auth.py           # JWT authentication
│   │   ├── workshops.py      # Workshop API
│   │   ├── participants.py   # Participant API
│   │   └── decorators.py     # JWT decorators
│   ├── services/             # Business logic layer
│   │   ├── workshop_service.py
│   │   └── participant_service.py
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html
│   │   ├── workshop/
│   │   └── observation/
│   └── static/
│       ├── css/
│       │   └── custom.css    # Minimalist design
│       └── js/
│           └── app.js        # AJAX interactions
├── frontend/                 # Vanilla JS SPA (NEW!)
│   ├── index.html            # Main application
│   ├── demo.html             # Demo landing page
│   ├── README.md             # Frontend documentation
│   ├── start-server.bat      # Windows launcher
│   ├── start-server.sh       # Unix launcher
│   ├── css/
│   │   └── styles.css        # Complete design system
│   └── js/
│       ├── config.js         # API configuration
│       ├── api.js            # HTTP client
│       ├── auth.js           # Authentication
│       ├── ui.js             # UI utilities
│       ├── workshops.js      # Workshop management
│       ├── participants.js   # Participant management
│       └── app.js            # Main entry point
├── tests/                    # Test suite
│   ├── conftest.py           # Pytest configuration
│   └── api/                  # API tests
│       ├── test_auth.py
│       ├── test_workshops.py
│       └── test_participants.py
├── .agent/                   # Agent documentation
│   ├── docs/                 # Additional documentation
│   │   ├── API.md            # API reference
│   │   ├── TESTING.md        # Testing guide
│   │   └── FRONTEND.md       # Frontend documentation
│   └── workflows/            # Development workflows
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── pytest.ini                # Test configuration
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

## API Usage

### Authentication

The API uses JWT (JSON Web Tokens) for authentication:

```bash
# Login to get JWT token
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response:
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "user": {...}
}
```

### API Endpoints

**Authentication:**
- `POST /api/v1/auth/login` - Login and get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

**Workshops:**
- `GET /api/v1/workshops` - List all workshops
- `POST /api/v1/workshops` - Create new workshop
- `GET /api/v1/workshops/{id}` - Get workshop details
- `PATCH /api/v1/workshops/{id}` - Update workshop
- `DELETE /api/v1/workshops/{id}` - Delete workshop

**Participants:**
- `GET /api/v1/participants/workshop/{id}` - List workshop participants
- `POST /api/v1/participants` - Create new participant
- `GET /api/v1/participants/{id}` - Get participant details
- `PATCH /api/v1/participants/{id}` - Update participant
- `DELETE /api/v1/participants/{id}` - Delete participant

### Example API Call

```bash
# Get all workshops (with authentication)
curl http://localhost:5000/api/v1/workshops \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### API Testing

Run the comprehensive test suite:

```bash
# Run all API tests
pytest tests/api/ -v

# Run specific test file
pytest tests/api/test_workshops.py -v

# Run with coverage
pytest tests/api/ --cov=app --cov-report=html
```

See `.agent/docs/TESTING.md` for detailed testing documentation.

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

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-flask

# Run all tests
pytest

# Run API tests only
pytest tests/api/ -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Creating Database Migrations

After modifying models:

```bash
flask --app run db migrate -m "Description of changes"
flask --app run db upgrade
```

### API Development

The API follows RESTful conventions:
- All API endpoints are under `/api/v1/`
- JWT authentication required for protected endpoints
- Service layer contains shared business logic
- CORS enabled for frontend development

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
