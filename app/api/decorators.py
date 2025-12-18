"""API decorators for JWT authentication."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User


def jwt_required_api(fn):
    """Require JWT authentication for API endpoints."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def admin_required_api(fn):
    """Require admin role for API endpoints."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())  # Convert from string to int
        user = User.query.get(user_id)
        
        if not user or not user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def get_current_api_user():
    """Get the current authenticated user from JWT token."""
    try:
        user_id = int(get_jwt_identity())  # Convert from string to int
        return User.query.get(user_id)
    except:
        return None
