---
description: Setup Development Environment
---

# Setup Development Environment

This workflow guides you through setting up the Arteterapia application from scratch.

## Prerequisites
- Python 3.8 or higher installed
- Git installed
- Terminal access

## Steps

### 1. Clone/Navigate to Repository
```bash
cd c:\Users\emi\Documents\GitHub\arteterapia_app
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
**Windows (PowerShell):**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

// turbo
### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Then edit `.env` and update:
- `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- Email configuration if needed

### 6. Initialize Database
**With sample data (recommended for development):**
```bash
python setup_db.py --with-data
```

**Without sample data:**
```bash
python setup_db.py
```

// turbo
### 7. Compile Translations
```bash
pybabel compile -d translations
```

// turbo
### 8. Run the Application
```bash
python run.py
```

### 9. Access the Application
Open your browser and navigate to:
- Main app: http://localhost:5000
- Admin panel: http://localhost:5000/admin
- Login with: `admin` / `admin123`

### 10. Change Default Password
**Important:** Navigate to http://localhost:5000/auth/change-password and change the default admin password immediately!

## Verification
- [ ] Application loads without errors
- [ ] Can log in with admin credentials
- [ ] Workshop list page displays
- [ ] Language switcher works (if enabled)
- [ ] Can access admin panel at /admin

## Troubleshooting
- If database locked error: Stop all Flask instances and restart
- If translations missing: Run `pybabel compile -d translations`
- If dependencies fail: Ensure Python version is 3.8+
