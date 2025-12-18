"""Workshop API endpoints (JSON responses)."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.api.decorators import jwt_required_api
from app.services.workshop_service import WorkshopService

workshops_api_bp = Blueprint('workshops_api', __name__, url_prefix='/workshops')


@workshops_api_bp.route('', methods=['GET'])
@jwt_required_api
def list_workshops():
    """
    GET /api/v1/workshops
    Returns: [{"id": 1, "name": "...", "objective": "...", ...}]
    """
    user_id = int(get_jwt_identity())  # Convert from string to int
    workshops = WorkshopService.get_user_workshops(user_id)
    
    return jsonify([w.to_dict() for w in workshops]), 200


@workshops_api_bp.route('', methods=['POST'])
@jwt_required_api
def create_workshop():
    """
    POST /api/v1/workshops
    Request: {"name": "Workshop Name", "objective": "..."}
    Response: {"id": 1, "name": "...", ...}
    """
    user_id = int(get_jwt_identity())  # Convert from string to int
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Workshop name is required'}), 400
    
    try:
        workshop = WorkshopService.create_workshop(
            user_id=user_id,
            name=data.get('name'),
            objective=data.get('objective')
        )
        
        return jsonify(workshop.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create workshop', 'message': str(e)}), 500


@workshops_api_bp.route('/<int:workshop_id>', methods=['GET'])
@jwt_required_api
def get_workshop(workshop_id):
    """
    GET /api/v1/workshops/123
    Response: {"id": 123, "name": "...", "participants": [...], "sessions": [...]}
    """
    user_id = int(get_jwt_identity())  # Convert from string to int
    workshop = WorkshopService.get_workshop(workshop_id, user_id)
    
    if not workshop:
        return jsonify({'error': 'Workshop not found or access denied'}), 404
    
    # Include relations (participants and sessions)
    return jsonify(workshop.to_dict(include_relations=True)), 200


@workshops_api_bp.route('/<int:workshop_id>', methods=['PUT', 'PATCH'])
@jwt_required_api
def update_workshop(workshop_id):
    """
    PUT/PATCH /api/v1/workshops/123
    Request: {"name": "New Name", "objective": "New Objective"}
    """
    user_id = int(get_jwt_identity())  # Convert from string to int
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        workshop = WorkshopService.update_workshop(workshop_id, user_id, data)
        
        if not workshop:
            return jsonify({'error': 'Workshop not found or access denied'}), 404
        
        return jsonify(workshop.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update workshop', 'message': str(e)}), 500


@workshops_api_bp.route('/<int:workshop_id>', methods=['DELETE'])
@jwt_required_api
def delete_workshop(workshop_id):
    """DELETE /api/v1/workshops/123"""
    user_id = int(get_jwt_identity())  # Convert from string to int
    
    try:
        success = WorkshopService.delete_workshop(workshop_id, user_id)
        
        if not success:
            return jsonify({'error': 'Workshop not found or access denied'}), 404
        
        return jsonify({'message': 'Workshop deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete workshop', 'message': str(e)}), 500
