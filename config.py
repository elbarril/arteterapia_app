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
    
    # Flask-Admin configuration
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # Bootstrap configuration
    BOOTSTRAP_SERVE_LOCAL = False
    BOOTSTRAP_BTN_STYLE = 'primary'
    BOOTSTRAP_BTN_SIZE = 'md'
    
    # Flask-Login configuration
    LOGIN_DISABLED = False
    REMEMBER_COOKIE_DURATION = 2592000  # 30 days in seconds
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Password reset and invitation settings
    PASSWORD_RESET_EXPIRY_HOURS = 24
    INVITATION_EXPIRY_DAYS = 7
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@arteterapia.local')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'true').lower() == 'true'  # Log to console in dev


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
