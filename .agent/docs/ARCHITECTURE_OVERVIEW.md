# Arteterapia - Complete Architecture Overview

## 🎯 Three Ways to Access the Application

```
┌─────────────────────────────────────────────────────────────────┐
│                    Arteterapia Application                       │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │              │    │              │    │              │      │
│  │  Web App     │    │  REST API    │    │  Frontend    │      │
│  │  (Jinja2)    │    │  (JSON)      │    │  SPA (JS)    │      │
│  │              │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│       ↓                     ↓                     ↓             │
│  Server-Side          JWT Tokens           Client-Side          │
│  Rendering            API Calls            Rendering            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Service Layer   │
                    │  (Business Logic)│
                    └──────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  SQLAlchemy ORM  │
                    └──────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Database        │
                    │  (SQLite/PG/MY)  │
                    └──────────────────┘
```

---

## 📊 Feature Comparison

| Feature | Web App | REST API | Frontend SPA |
|---------|---------|----------|--------------|
| **Technology** | Flask + Jinja2 | Flask + JWT | Vanilla JS |
| **Authentication** | Session Cookies | JWT Tokens | JWT Tokens |
| **Rendering** | Server-Side | N/A (JSON) | Client-Side |
| **Page Loads** | Full Reload | N/A | No Reload (SPA) |
| **Workshops CRUD** | ✅ | ✅ | ✅ |
| **Participants CRUD** | ✅ | ✅ | ✅ |
| **Sessions CRUD** | ✅ | ⏳ Planned | ⏳ Planned |
| **Observations** | ✅ | ⏳ Planned | ⏳ Planned |
| **Admin Panel** | ✅ | ❌ | ❌ |
| **Mobile Friendly** | ✅ | ✅ | ✅ |
| **Offline Support** | ❌ | ❌ | 🔄 Possible |
| **External Integration** | ❌ | ✅ | ✅ |

---

## 🚀 Quick Start Guide

### Option 1: Traditional Web App
```bash
# Start backend
python run.py

# Open browser
http://localhost:5000

# Login: admin / admin123
```

### Option 2: REST API
```bash
# Start backend
python run.py

# Test with curl
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token for API calls
curl http://localhost:5000/api/v1/workshops \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Option 3: Frontend SPA
```bash
# Terminal 1: Start backend
python run.py

# Terminal 2: Start frontend
cd frontend
python -m http.server 8000

# Open browser
http://localhost:8000/demo.html

# Login: admin / admin123
```

---

## 📁 Project Structure at a Glance

```
arteterapia_app/
├── 🌐 app/                    # Backend application
│   ├── models/                # Database models
│   ├── routes/                # Web routes (Jinja2)
│   ├── api/                   # REST API routes (JSON)
│   ├── services/              # Business logic
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS for web app
│
├── 💻 frontend/               # Frontend SPA (NEW!)
│   ├── index.html             # Main app
│   ├── demo.html              # Landing page
│   ├── css/styles.css         # Design system
│   └── js/                    # Vanilla JavaScript
│       ├── api.js             # HTTP client
│       ├── auth.js            # Authentication
│       ├── workshops.js       # Workshop management
│       └── participants.js    # Participant management
│
├── 🧪 tests/                  # Test suite
│   └── api/                   # API tests (pytest)
│
├── 📚 .agent/                 # Documentation
│   ├── docs/
│   │   ├── API.md             # API reference
│   │   ├── TESTING.md         # Testing guide
│   │   └── FRONTEND.md        # Frontend guide
│   └── workflows/             # Development workflows
│
└── 🔧 config files
    ├── config.py              # App configuration
    ├── requirements.txt       # Python dependencies
    └── run.py                 # Entry point
```

---

## 🎨 Design Philosophy

All three interfaces follow the same design principles:

- ✅ **Minimalist**: Clean, uncluttered interface
- ✅ **Brand Colors**: Applied to borders, shadows, accents
- ✅ **Responsive**: Mobile-first design
- ✅ **Accessible**: Keyboard navigation, focus states
- ✅ **Consistent**: Same UX across all interfaces

---

## 🔐 Authentication Flow

### Web App (Session-based)
```
User Login → Flask-Login → Session Cookie → Protected Routes
```

### API + Frontend (JWT-based)
```
User Login → JWT Tokens → localStorage → API Calls with Bearer Token
                ↓
         Access Token (15 min)
         Refresh Token (30 days)
                ↓
         Auto-refresh on 401
```

---

## 📈 Development Timeline

### ✅ Phase 1: Core Application (Completed)
- Flask application with Jinja2 templates
- Workshop, Participant, Session, Observation models
- Complete CRUD operations
- Flask-Admin panel
- Authentication system

### ✅ Phase 2: API Layer (Completed)
- RESTful JSON API
- JWT authentication
- Service layer
- Comprehensive test suite (45 tests)
- API documentation

### ✅ Phase 3: Frontend SPA (Completed - December 2025)
- Vanilla JavaScript SPA
- Zero dependencies
- Complete UI with modals, toasts
- Workshops and Participants CRUD
- Responsive design

### 🔄 Phase 4: Future Enhancements (Planned)
- Sessions API + Frontend
- Observations API + Frontend
- Search and filters
- Data export (CSV, PDF)
- Real-time updates (WebSockets)
- Progressive Web App (PWA)

---

## 🛠️ Technology Stack Summary

### Backend
- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy
- **Migrations**: Alembic (Flask-Migrate)
- **Admin**: Flask-Admin
- **API Auth**: Flask-JWT-Extended
- **CORS**: Flask-CORS
- **Testing**: pytest

### Frontend (Web App)
- **Templates**: Jinja2
- **CSS**: Bootstrap 5 + Custom CSS
- **JavaScript**: Vanilla JS + AJAX

### Frontend (SPA)
- **HTML**: Semantic HTML5
- **CSS**: Custom design system (CSS variables)
- **JavaScript**: Pure Vanilla JS (ES6+)
- **Dependencies**: Zero! 🎉

### Database
- **Development**: SQLite
- **Production**: PostgreSQL / MySQL ready

---

## 📊 Code Statistics

| Component | Files | Lines of Code | Dependencies |
|-----------|-------|---------------|--------------|
| Backend Core | ~30 | ~3,000 | Flask, SQLAlchemy |
| API Layer | ~10 | ~1,500 | JWT, CORS |
| Web Templates | ~15 | ~2,000 | Jinja2, Bootstrap |
| Frontend SPA | ~11 | ~2,000 | **Zero!** |
| Tests | ~10 | ~1,500 | pytest |
| **Total** | **~76** | **~10,000** | Minimal |

---

## 🎯 Use Cases

### Use Case 1: Art Therapist (Web App)
*"I want a simple interface to manage my workshops"*
- ✅ Use the traditional web app
- ✅ Server-rendered, fast, reliable
- ✅ No technical knowledge required

### Use Case 2: Mobile App Developer (API)
*"I want to build a mobile app for therapists"*
- ✅ Use the REST API
- ✅ JWT authentication
- ✅ Complete CRUD operations
- ✅ Well-documented endpoints

### Use Case 3: Modern Web Developer (Frontend SPA)
*"I want a fast, modern interface"*
- ✅ Use the Frontend SPA
- ✅ No page reloads
- ✅ Smooth animations
- ✅ Can be deployed separately

### Use Case 4: Institution (All Three)
*"We need flexibility for different users"*
- ✅ Therapists use Web App
- ✅ Researchers use API for data analysis
- ✅ Students use Frontend SPA
- ✅ All share the same database

---

## 🔒 Security Features

- ✅ Password hashing (Werkzeug)
- ✅ JWT token authentication
- ✅ CSRF protection (web app)
- ✅ XSS prevention (HTML escaping)
- ✅ SQL injection protection (ORM)
- ✅ CORS configuration
- ✅ Environment variables for secrets
- ✅ Token expiration and refresh

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | Main project documentation |
| `frontend/README.md` | Frontend SPA guide |
| `.agent/AGENT_GUIDELINES.md` | Comprehensive dev guide |
| `.agent/QUICK_REFERENCE.md` | Quick lookup |
| `.agent/docs/API.md` | API reference |
| `.agent/docs/TESTING.md` | Testing guide |
| `.agent/docs/FRONTEND.md` | Frontend architecture |

---

## 🎉 Summary

The Arteterapia application now offers **three complete interfaces** for managing art therapy workshops:

1. **Traditional Web App** - Reliable, server-rendered
2. **REST API** - Flexible, integration-ready
3. **Frontend SPA** - Modern, fast, responsive

All three share the same:
- ✅ Database
- ✅ Business logic
- ✅ Security model
- ✅ Design principles

**Choose the interface that fits your needs, or use all three!**

---

*Last Updated: December 17, 2025*
