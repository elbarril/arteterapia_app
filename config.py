import os
from pathlib import Path

basedir = Path(__file__).parent


class Config:
    """Base configuration class."""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - SQLite for development, easily portable to PostgreSQL/MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{basedir / "arteterapia.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Babel configuration
    BABEL_DEFAULT_LOCALE = 'es'  # Spanish as default
    BABEL_DEFAULT_TIMEZONE = 'America/Argentina/Buenos_Aires'
    LANGUAGES = {
        'es': 'Español',
        'en': 'English'
    }
    
    # Flask-Admin configuration
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # Bootstrap configuration
    BOOTSTRAP_SERVE_LOCAL = False
    BOOTSTRAP_BTN_STYLE = 'primary'
    BOOTSTRAP_BTN_SIZE = 'md'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
