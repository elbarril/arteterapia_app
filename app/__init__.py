"""Flask application factory."""
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_babel import Babel
from flask_bootstrap import Bootstrap5
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
admin = Admin(name='Arteterapia Admin', template_mode='bootstrap4')
babel = Babel()
bootstrap = Bootstrap5()


def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    
    # Initialize Babel with locale selector
    def get_locale():
        """Select best language match from client preferences."""
        return request.accept_languages.best_match(
            app.config['LANGUAGES'].keys()
        ) or app.config['BABEL_DEFAULT_LOCALE']
    
    babel.init_app(app, locale_selector=get_locale)
    
    # Register blueprints first
    from app.controllers.workshop import workshop_bp
    from app.controllers.participant import participant_bp
    from app.controllers.session import session_bp
    from app.controllers.observation import observation_bp
    
    app.register_blueprint(workshop_bp)
    app.register_blueprint(participant_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(observation_bp)
    
    # Import models for Flask-Migrate and Flask-Admin
    from app.models.workshop import Workshop
    from app.models.participant import Participant
    from app.models.session import Session
    from app.models.observation import ObservationalRecord
    from flask_admin.contrib.sqla import ModelView
    
    
    # Initialize Flask-Admin
    admin.init_app(app)
    
    admin.add_view(ModelView(Workshop, db.session, name='Talleres'))
    admin.add_view(ModelView(Participant, db.session, name='Participantes'))
    admin.add_view(ModelView(Session, db.session, name='Sesiones'))
    admin.add_view(ModelView(ObservationalRecord, db.session, name='Registros'))
    
    return app
