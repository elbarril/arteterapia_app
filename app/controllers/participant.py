"""Participant controller."""
from flask import Blueprint, request, jsonify
from flask_babel import gettext as _
from flask_login import login_required
from app import db
from app.models.participant import Participant
from app.models.workshop import Workshop

participant_bp = Blueprint('participant_bp', __name__)


@participant_bp.route('/workshop/<int:workshop_id>/participant/create', methods=['POST'])
@login_required
def create_participant(workshop_id):
    """Create a new participant for a workshop (AJAX)."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({
            'success': False,
            'message': _('El nombre es obligatorio')
        }), 400
    
    participant = Participant(name=name, workshop_id=workshop_id)
    db.session.add(participant)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Participante agregado'),
        'participant': {
            'id': participant.id,
            'name': participant.name
        },
        'participant_count': workshop.participant_count
    })


@participant_bp.route('/participant/<int:participant_id>/update', methods=['PUT', 'POST'])
@login_required
def update_participant(participant_id):
    """Update a participant (AJAX)."""
    participant = Participant.query.get_or_404(participant_id)
    
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({
            'success': False,
            'message': _('El nombre es obligatorio')
        }), 400
    
    participant.name = name
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Participante actualizado'),
        'participant': {
            'id': participant.id,
            'name': participant.name
        }
    })


@participant_bp.route('/participant/<int:participant_id>/delete', methods=['DELETE', 'POST'])
@login_required
def delete_participant(participant_id):
    """Delete a participant (AJAX)."""
    participant = Participant.query.get_or_404(participant_id)
    workshop_id = participant.workshop_id
    
    db.session.delete(participant)
    db.session.commit()
    
    workshop = Workshop.query.get(workshop_id)
    
    return jsonify({
        'success': True,
        'message': _('Participante eliminado'),
        'participant_count': workshop.participant_count
    })
