"""Observation API endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.api.decorators import jwt_required_api
from app.services.observation_service import ObservationService
from app.models.observation_questions import (
    get_all_questions, get_question_by_index, get_total_question_count,
    ANSWER_OPTIONS, OBSERVATION_CATEGORIES
)

observations_api_bp = Blueprint('observations_api', __name__, url_prefix='/observations')


@observations_api_bp.route('/workshop/<int:workshop_id>', methods=['GET'])
@jwt_required_api
def list_workshop_observations(workshop_id):
    """
    GET /api/v1/observations/workshop/{workshop_id}
    
    Get all observations for a workshop.
    
    Response: [
        {
            "id": 1,
            "session_id": 1,
            "participant_id": 1,
            "version": 1,
            "answers": {...},
            "freeform_notes": "...",
            "created_at": "..."
        }
    ]
    """
    user_id = int(get_jwt_identity())
    observations, error = ObservationService.get_workshop_observations(workshop_id, user_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    # Convert to dict (ObservationalRecord doesn't have to_dict, so we'll create it)
    result = []
    for obs in observations:
        result.append({
            'id': obs.id,
            'session_id': obs.session_id,
            'participant_id': obs.participant_id,
            'version': obs.version,
            'answers': obs.answers,
            'freeform_notes': obs.freeform_notes,
            'created_at': obs.created_at.isoformat() if obs.created_at else None
        })
    
    return jsonify(result), 200


@observations_api_bp.route('/<int:observation_id>', methods=['GET'])
@jwt_required_api
def get_observation(observation_id):
    """
    GET /api/v1/observations/{observation_id}
    
    Get single observation details.
    
    Response: {
        "id": 1,
        "session_id": 1,
        "participant_id": 1,
        "version": 1,
        "answers": {...},
        "freeform_notes": "...",
        "created_at": "..."
    }
    """
    user_id = int(get_jwt_identity())
    observation, error = ObservationService.get_observation(observation_id, user_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({
        'id': observation.id,
        'session_id': observation.session_id,
        'participant_id': observation.participant_id,
        'version': observation.version,
        'answers': observation.answers,
        'freeform_notes': observation.freeform_notes,
        'created_at': observation.created_at.isoformat() if observation.created_at else None
    }), 200


@observations_api_bp.route('/initialize', methods=['POST'])
@jwt_required_api
def initialize_observation():
    """
    POST /api/v1/observations/initialize
    
    Initialize a new observation session.
    
    Request: {
        "session_id": 1,
        "participant_id": 1
    }
    Response: {
        "observation_data": {
            "session_id": 1,
            "participant_id": 1,
            "answers": {...},  // Pre-filled from previous observation if exists
            "current_index": 0,
            "is_redo": false,
            "previous_version": 0
        },
        "first_question": {...},
        "total_questions": 50
    }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    session_id = data.get('session_id')
    participant_id = data.get('participant_id')
    
    if not session_id or not participant_id:
        return jsonify({'error': 'Session ID and Participant ID are required'}), 400
    
    observation_data, error = ObservationService.initialize_observation(
        session_id,
        participant_id,
        user_id
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    # Get first question
    first_question = get_question_by_index(0)
    
    return jsonify({
        'observation_data': observation_data,
        'first_question': {
            'id': first_question['id'],
            'text': str(first_question['text']),
            'category': str(first_question['category']),
            'subcategory': str(first_question['subcategory']) if first_question['subcategory'] else None
        },
        'total_questions': get_total_question_count()
    }), 200


@observations_api_bp.route('/save', methods=['POST'])
@jwt_required_api
def save_observation():
    """
    POST /api/v1/observations/save
    
    Save a completed observation.
    
    Request: {
        "observation_data": {
            "session_id": 1,
            "participant_id": 1,
            "answers": {...},
            "previous_version": 0
        },
        "freeform_notes": "Optional notes"
    }
    Response: {
        "id": 1,
        "message": "Observation saved successfully",
        "version": 1
    }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request format'}), 400
    
    observation_data = data.get('observation_data')
    freeform_notes = data.get('freeform_notes', '')
    
    if not observation_data:
        return jsonify({'error': 'Observation data is required'}), 400
    
    record, error = ObservationService.save_observation(
        observation_data,
        freeform_notes,
        user_id
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'id': record.id,
        'message': 'Observation saved successfully',
        'version': record.version
    }), 201


@observations_api_bp.route('/<int:observation_id>', methods=['DELETE'])
@jwt_required_api
def delete_observation(observation_id):
    """
    DELETE /api/v1/observations/{observation_id}
    
    Delete an observation.
    
    Response: {"message": "Observation deleted successfully"}
    """
    user_id = int(get_jwt_identity())
    
    success, error = ObservationService.delete_observation(observation_id, user_id)
    
    if not success:
        return jsonify({'error': error or 'Failed to delete observation'}), 404
    
    return jsonify({'message': 'Observation deleted successfully'}), 200


@observations_api_bp.route('/questions', methods=['GET'])
@jwt_required_api
def get_questions():
    """
    GET /api/v1/observations/questions
    
    Get all observation questions.
    
    Response: {
        "questions": [...],
        "categories": [...],
        "answer_options": [...]
    }
    """
    questions = get_all_questions()
    
    # Convert lazy strings to regular strings for JSON serialization
    serializable_questions = []
    for q in questions:
        serializable_questions.append({
            'id': q['id'],
            'text': str(q['text']),
            'category': str(q['category']),
            'subcategory': str(q['subcategory']) if q['subcategory'] else None
        })
    
    return jsonify({
        'questions': serializable_questions,
        'categories': [str(cat) for cat in OBSERVATION_CATEGORIES],
        'answer_options': ANSWER_OPTIONS,
        'total_count': get_total_question_count()
    }), 200


@observations_api_bp.route('/questions/<int:index>', methods=['GET'])
@jwt_required_api
def get_question_by_idx(index):
    """
    GET /api/v1/observations/questions/{index}
    
    Get a specific question by index.
    
    Response: {
        "id": "question_id",
        "text": "Question text",
        "category": "Category",
        "subcategory": "Subcategory or null"
    }
    """
    if index < 0 or index >= get_total_question_count():
        return jsonify({'error': 'Invalid question index'}), 400
    
    question = get_question_by_index(index)
    
    return jsonify({
        'id': question['id'],
        'text': str(question['text']),
        'category': str(question['category']),
        'subcategory': str(question['subcategory']) if question['subcategory'] else None,
        'index': index,
        'total': get_total_question_count()
    }), 200
