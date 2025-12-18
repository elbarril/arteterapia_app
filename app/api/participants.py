"""Participant API endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.api.decorators import jwt_required_api
from app.services.participant_service import ParticipantService


participants_api_bp = Blueprint('participants_api', __name__, url_prefix='/participants')


@participants_api_bp.route('/workshop/<int:workshop_id>', methods=['GET'])
@jwt_required_api
def list_participants(workshop_id):
    """
    GET /api/v1/participants/workshop/{workshop_id}
    Returns: [{"id": 1, "name": "...", "workshop_id": 1, ...}]
    """
    user_id = int(get_jwt_identity())
    participants = ParticipantService.get_workshop_participants(workshop_id, user_id)
    
    if participants is None:
        return jsonify({'error': 'Workshop not found or access denied'}), 404
    
    return jsonify([p.to_dict() for p in participants]), 200


@participants_api_bp.route('', methods=['POST'])
@jwt_required_api
def create_participant():
    """
    POST /api/v1/participants
    Request: {"workshop_id": 1, "name": "Participant Name", "extra_data": {...}}
    Response: {"id": 1, "name": "...", ...}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('workshop_id') or not data.get('name'):
        return jsonify({'error': 'Workshop ID and name are required'}), 400
    
    try:
        participant = ParticipantService.create_participant(
            workshop_id=data.get('workshop_id'),
            user_id=user_id,
            name=data.get('name'),
            extra_data=data.get('extra_data')
        )
        
        if not participant:
            return jsonify({'error': 'Workshop not found or access denied'}), 404
        
        return jsonify(participant.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create participant', 'message': str(e)}), 500


@participants_api_bp.route('/<int:participant_id>', methods=['GET'])
@jwt_required_api
def get_participant(participant_id):
    """
    GET /api/v1/participants/123
    Response: {"id": 123, "name": "...", ...}
    """
    user_id = int(get_jwt_identity())
    participant = ParticipantService.get_participant(participant_id, user_id)
    
    if not participant:
        return jsonify({'error': 'Participant not found or access denied'}), 404
    
    return jsonify(participant.to_dict()), 200


@participants_api_bp.route('/<int:participant_id>', methods=['PUT', 'PATCH'])
@jwt_required_api
def update_participant(participant_id):
    """
    PUT/PATCH /api/v1/participants/123
    Request: {"name": "New Name", "extra_data": {...}}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        participant = ParticipantService.update_participant(participant_id, user_id, data)
        
        if not participant:
            return jsonify({'error': 'Participant not found or access denied'}), 404
        
        return jsonify(participant.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update participant', 'message': str(e)}), 500


@participants_api_bp.route('/<int:participant_id>', methods=['DELETE'])
@jwt_required_api
def delete_participant(participant_id):
    """DELETE /api/v1/participants/123"""
    user_id = int(get_jwt_identity())
    
    try:
        success = ParticipantService.delete_participant(participant_id, user_id)
        
        if not success:
            return jsonify({'error': 'Participant not found or access denied'}), 404
        
        return jsonify({'message': 'Participant deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete participant', 'message': str(e)}), 500
