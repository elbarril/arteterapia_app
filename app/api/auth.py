"""API authentication endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from app.models.user import User
from app.api.decorators import jwt_required_api

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/auth')


@auth_api_bp.route('/login', methods=['POST'])
def api_login():
    """
    Authenticate and return JWT tokens.
    
    Request: {"username": "...", "password": "..."}
    Response: {"access_token": "...", "refresh_token": "...", "user": {...}}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.active:
        return jsonify({'error': 'Account is not active'}), 403
    
    if not user.email_verified:
        return jsonify({'error': 'Email not verified'}), 403
    
    # Create JWT tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    """
    Refresh access token using refresh token.
    
    Headers: Authorization: Bearer <refresh_token>
    Response: {"access_token": "..."}
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': new_access_token
    }), 200


@auth_api_bp.route('/me', methods=['GET'])
@jwt_required_api
def api_current_user():
    """
    Get current authenticated user information.
    
    Headers: Authorization: Bearer <access_token>
    Response: {"id": 1, "username": "...", ...}
    """
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))  # Convert back to int for query
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200
