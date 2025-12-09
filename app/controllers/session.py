"""Session controller."""
from flask import Blueprint, request, jsonify
from flask_babel import gettext as _
from flask_login import login_required
from app import db
from app.models.session import Session
from app.models.workshop import Workshop

session_bp = Blueprint('session_bp', __name__)


@session_bp.route('/workshop/<int:workshop_id>/session/create', methods=['POST'])
@login_required
def create_session(workshop_id):
    """Create a new session for a workshop (AJAX)."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    motivation = data.get('motivation', '').strip()
    materials_raw = data.get('materials', '').strip()
    
    if not prompt:
        return jsonify({
            'success': False,
            'message': _('La consigna es obligatoria')
        }), 400
    
    # Parse materials as comma-separated list
    materials = [m.strip() for m in materials_raw.split(',') if m.strip()] if materials_raw else []
    
    session = Session(
        workshop_id=workshop_id,
        prompt=prompt,
        motivation=motivation or None,
        materials=materials if materials else None
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Sesión creada'),
        'session': {
            'id': session.id,
            'prompt': session.prompt,
            'motivation': session.motivation,
            'materials': session.materials,
            'observation_count': session.observation_count
        },
        'session_count': workshop.session_count
    })


@session_bp.route('/session/<int:session_id>/update', methods=['PUT', 'POST'])
@login_required
def update_session(session_id):
    """Update a session (AJAX)."""
    session = Session.query.get_or_404(session_id)
    
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    motivation = data.get('motivation', '').strip()
    materials_raw = data.get('materials', '').strip()
    
    if not prompt:
        return jsonify({
            'success': False,
            'message': _('La consigna es obligatoria')
        }), 400
    
    # Parse materials as comma-separated list
    materials = [m.strip() for m in materials_raw.split(',') if m.strip()] if materials_raw else []
    
    session.prompt = prompt
    session.motivation = motivation or None
    session.materials = materials if materials else None
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Sesión actualizada'),
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
    session = Session.query.get_or_404(session_id)
    workshop_id = session.workshop_id
    
    db.session.delete(session)
    db.session.commit()
    
    workshop = Workshop.query.get(workshop_id)
    
    return jsonify({
        'success': True,
        'message': _('Sesión eliminada'),
        'session_count': workshop.session_count
    })
