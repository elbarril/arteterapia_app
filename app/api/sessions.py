"""Session API endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.api.decorators import jwt_required_api
from app.services.session_service import SessionService

sessions_api_bp = Blueprint('sessions_api', __name__, url_prefix='/sessions')


@sessions_api_bp.route('/workshop/<int:workshop_id>', methods=['GET'])
@jwt_required_api
def list_sessions(workshop_id):
    """
    GET /api/v1/sessions/workshop/{workshop_id}
    
    Get all sessions for a workshop.
    
    Response: [{"id": 1, "prompt": "...", "motivation": "...", "materials": [...], ...}]
    """
    user_id = int(get_jwt_identity())
    sessions = SessionService.get_workshop_sessions(workshop_id, user_id)
    
    if sessions is None:
        return jsonify({'error': 'Workshop not found or access denied'}), 404
    
    return jsonify([s.to_dict() for s in sessions]), 200


@sessions_api_bp.route('/<int:session_id>', methods=['GET'])
@jwt_required_api
def get_session(session_id):
    """
    GET /api/v1/sessions/{session_id}
    
    Get single session details.
    
    Response: {"id": 1, "prompt": "...", ...}
    """
    user_id = int(get_jwt_identity())
    session = SessionService.get_session(session_id, user_id)
    
    if not session:
        return jsonify({'error': 'Session not found or access denied'}), 404
    
    return jsonify(session.to_dict()), 200


@sessions_api_bp.route('', methods=['POST'])
@jwt_required_api
def create_session():
    """
    POST /api/v1/sessions
    
    Create a new session.
    
    Request: {
        "workshop_id": 1,
        "prompt": "Session prompt",
        "motivation": "Optional motivation",
        "materials": "comma,separated,materials" or ["material1", "material2"]
    }
    Response: {"id": 1, "prompt": "...", ...}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    workshop_id = data.get('workshop_id')
    prompt = data.get('prompt')
    motivation = data.get('motivation')
    materials = data.get('materials')
    
    if not workshop_id or not prompt:
        return jsonify({'error': 'Workshop ID and prompt are required'}), 400
    
    try:
        session = SessionService.create_session(
            workshop_id=workshop_id,
            user_id=user_id,
            prompt=prompt,
            motivation=motivation,
            materials=materials
        )
        
        if not session:
            return jsonify({'error': 'Workshop not found or access denied'}), 404
        
        return jsonify(session.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create session', 'message': str(e)}), 500


@sessions_api_bp.route('/<int:session_id>', methods=['PUT', 'PATCH'])
@jwt_required_api
def update_session(session_id):
    """
    PUT/PATCH /api/v1/sessions/{session_id}
    
    Update a session.
    
    Request: {
        "prompt": "Updated prompt",
        "motivation": "Updated motivation",
        "materials": "updated,materials"
    }
    Response: {"id": 1, "prompt": "...", ...}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        session = SessionService.update_session(session_id, user_id, data)
        
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        return jsonify(session.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update session', 'message': str(e)}), 500


@sessions_api_bp.route('/<int:session_id>', methods=['DELETE'])
@jwt_required_api
def delete_session(session_id):
    """
    DELETE /api/v1/sessions/{session_id}
    
    Delete a session.
    
    Response: {"message": "Session deleted successfully", "workshop_id": 1}
    """
    user_id = int(get_jwt_identity())
    
    try:
        result = SessionService.delete_session(session_id, user_id)
        
        if not result:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        return jsonify({
            'message': 'Session deleted successfully',
            'workshop_id': result['workshop_id']
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete session', 'message': str(e)}), 500
