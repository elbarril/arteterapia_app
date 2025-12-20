"""Session controller."""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.services.session_service import SessionService

session_bp = Blueprint('session_bp', __name__)


@session_bp.route('/workshop/<int:workshop_id>/session/create', methods=['POST'])
@login_required
def create_session(workshop_id):
    """Create a new session for a workshop (AJAX)."""
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    motivation = data.get('motivation', '').strip()
    materials_raw = data.get('materials', '').strip()
    
    # Validation
    if not prompt:
        return jsonify({
            'success': False,
            'message': 'La consigna es obligatoria'
        }), 400
    
    # Use service to create session (includes permission check)
    session = SessionService.create_session(
        workshop_id=workshop_id,
        user_id=current_user.id,
        prompt=prompt,
        motivation=motivation or None,
        materials=materials_raw
    )
    
    if not session:
        return jsonify({
            'success': False,
            'message': 'Taller no encontrado o sin permiso'
        }), 404
    
    return jsonify({
        'success': True,
        'message': 'Sesión creada',
        'session': {
            'id': session.id,
            'prompt': session.prompt,
            'motivation': session.motivation,
            'materials': session.materials,
            'observation_count': session.observation_count
        },
        'session_count': session.workshop.session_count
    })


@session_bp.route('/session/<int:session_id>/update', methods=['PUT', 'POST'])
@login_required
def update_session(session_id):
    """Update a session (AJAX)."""
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    
    # Validation
    if not prompt:
        return jsonify({
            'success': False,
            'message': 'La consigna es obligatoria'
        }), 400
    
    # Use service to update session (includes permission check)
    session = SessionService.update_session(
        session_id=session_id,
        user_id=current_user.id,
        data={
            'prompt': prompt,
            'motivation': data.get('motivation', '').strip() or None,
            'materials': data.get('materials', '').strip()
        }
    )
    
    if not session:
        return jsonify({
            'success': False,
            'message': 'Sesión no encontrada o sin permiso'
        }), 404
    
    return jsonify({
        'success': True,
        'message': 'Sesión actualizada',
        'session': {
            'id': session.id,
            'prompt': session.prompt,
            'motivation': session.motivation,
            'materials': session.materials,
            'observation_count': session.observation_count
        }
    })


@session_bp.route('/session/<int:session_id>/delete', methods=['DELETE', 'POST'])
@login_required
def delete_session(session_id):
    """Delete a session (AJAX)."""
    # Use service to delete session (includes permission check)
    result = SessionService.delete_session(
        session_id=session_id,
        user_id=current_user.id
    )
    
    if not result:
        return jsonify({
            'success': False,
            'message': 'Sesión no encontrada o sin permiso'
        }), 404
    
    # Get workshop for session count
    from app.models.workshop import Workshop
    workshop = Workshop.query.get(result['workshop_id'])
    
    return jsonify({
        'success': True,
        'message': 'Sesión eliminada',
        'session_count': workshop.session_count if workshop else 0
    })
