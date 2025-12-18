"""Flask application factory."""
from flask import Flask, request, redirect, url_for, flash, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
admin = Admin(name='Arteterapia Admin', template_mode='bootstrap4')
bootstrap = Bootstrap5()
login_manager = LoginManager()


# Custom admin index view with authentication check
class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login if not authenticated, or home if not admin."""
        if current_user.is_authenticated:
            # User is logged in but not an admin, redirect to home
            flash('No tienes permiso para acceder al panel de administración.', 'danger')
            return redirect(url_for('workshop_bp.list_workshops'))
        # User is not logged in, redirect to login
        return redirect(url_for('auth_bp.login', next=request.url))


def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Initialize Flask-Mail
    from app.utils.email_utils import mail
    mail.init_app(app)
    
    # Initialize JWT for API authentication
    from flask_jwt_extended import JWTManager
    jwt = JWTManager()
    jwt.init_app(app)
    
    # Initialize CORS for API endpoints only
    from flask_cors import CORS
    CORS(app, resources={r"/api/v1/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    

    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.workshop import workshop_bp
    from app.routes.participant import participant_bp
    from app.routes.session import session_bp
    from app.routes.observation import observation_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(workshop_bp)
    app.register_blueprint(participant_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(observation_bp)
    
    # Register API blueprint
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Import models for Flask-Migrate and Flask-Admin
    from app.models.workshop import Workshop
    from app.models.participant import Participant
    from app.models.session import Session
    from app.models.observation import ObservationalRecord
    from app.models.user import User
    from app.models.role import Role
    from app.models.user_invitation import UserInvitation
    
    # Import custom admin views
    from app.admin_views import (
        WorkshopAdminView,
        SessionAdminView,
        ParticipantAdminView,
        ObservationalRecordAdminView,
        UserAdminView,
        RoleAdminView,
        UserInvitationAdminView
    )
    
    # Initialize Flask-Admin with secure index view
    admin.init_app(app, index_view=SecureAdminIndexView())
    
    # Add admin views (all protected by role check in admin_views.py)
    admin.add_view(WorkshopAdminView(Workshop, db.session, name='Talleres'))
    admin.add_view(ParticipantAdminView(Participant, db.session, name='Participantes'))
    admin.add_view(SessionAdminView(Session, db.session, name='Sesiones'))
    admin.add_view(ObservationalRecordAdminView(ObservationalRecord, db.session, name='Registros'))
    admin.add_view(UserAdminView(User, db.session, name='Usuarios'))
    admin.add_view(RoleAdminView(Role, db.session, name='Roles'))
    admin.add_view(UserInvitationAdminView(UserInvitation, db.session, name='Invitaciones'))
    
    # Expose config to templates
    app.jinja_env.globals['config'] = app.config
    return app
