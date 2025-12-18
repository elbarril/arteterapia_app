"""Main API blueprint that aggregates all API routes."""
from flask import Blueprint

# Create main API blueprint with /api/v1 prefix
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import sub-blueprints
from app.api.auth import auth_api_bp
from app.api.workshops import workshops_api_bp
from app.api.participants import participants_api_bp

# Register sub-blueprints
api_bp.register_blueprint(auth_api_bp)
api_bp.register_blueprint(workshops_api_bp)
api_bp.register_blueprint(participants_api_bp)
