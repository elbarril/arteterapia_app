"""Observation controller."""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session as flask_session
from flask_babel import gettext as _
from app import db
from app.models.session import Session
from app.models.participant import Participant
from app.models.observation import ObservationalRecord
from app.models.observation_questions import (
    get_all_questions, get_question_by_index, get_total_question_count,
    ANSWER_OPTIONS, OBSERVATION_CATEGORIES
)

observation_bp = Blueprint('observation_bp', __name__)


@observation_bp.route('/session/<int:session_id>/observe/<int:participant_id>')
def start_observation(session_id, participant_id):
    """Start the observational record flow."""
    session_obj = Session.query.get_or_404(session_id)
    participant = Participant.query.get_or_404(participant_id)
    
    # Verify participant belongs to same workshop as session
    if participant.workshop_id != session_obj.workshop_id:
        return redirect(url_for('workshop_bp.detail', workshop_id=session_obj.workshop_id))
    
    # Initialize session data
    flask_session['observation_data'] = {
        'session_id': session_id,
        'participant_id': participant_id,
        'answers': {},
        'current_index': 0
    }
    
    # Get first question
    first_question = get_question_by_index(0)
    
    return render_template(
        'observation/create.html',
        session=session_obj,
        participant=participant,
        question=first_question,
        question_index=0,
        total_questions=get_total_question_count(),
        answer_options=ANSWER_OPTIONS
    )


@observation_bp.route('/observation/answer', methods=['POST'])
def process_answer():
    """Process an answer and move to the next question (AJAX)."""
    data = request.get_json()
    answer = data.get('answer')
    question_id = data.get('question_id')
    
    if 'observation_data' not in flask_session:
        return jsonify({'success': False, 'message': _('Sesión expirada')}), 400
    
    # Store answer
    obs_data = flask_session['observation_data']
    obs_data['answers'][question_id] = answer
    obs_data['current_index'] += 1
    flask_session['observation_data'] = obs_data
    
    # Check if there are more questions
    next_index = obs_data['current_index']
    total = get_total_question_count()
    
    if next_index < total:
        # Return next question
        next_question = get_question_by_index(next_index)
        return jsonify({
            'success': True,
            'has_more': True,
            'next_question': {
                'id': next_question['id'],
                'text': str(next_question['text']),
                'category': str(next_question['category']),
                'subcategory': str(next_question['subcategory']) if next_question['subcategory'] else None
            },
            'question_index': next_index,
            'total_questions': total
        })
    else:
        # All questions answered
        return jsonify({
            'success': True,
            'has_more': False,
            'message': _('Todas las preguntas respondidas')
        })


@observation_bp.route('/observation/complete', methods=['POST'])
def complete_observation():
    """Save the completed observation with optional freeform notes."""
    if 'observation_data' not in flask_session:
        return jsonify({'success': False, 'message': _('Sesión expirada')}), 400
    
    data = request.get_json()
    freeform_notes = data.get('freeform_notes', '').strip()
    
    obs_data = flask_session['observation_data']
    
    # Create observational record
    record = ObservationalRecord(
        session_id=obs_data['session_id'],
        participant_id=obs_data['participant_id'],
        answers=obs_data['answers'],
        freeform_notes=freeform_notes if freeform_notes else None
    )
    db.session.add(record)
    db.session.commit()
    
    # Clear session data
    flask_session.pop('observation_data', None)
    
    # Get workshop ID for redirect
    session_obj = Session.query.get(obs_data['session_id'])
    
    return jsonify({
        'success': True,
        'message': _('Registro guardado exitosamente'),
        'redirect_url': url_for('workshop_bp.detail', workshop_id=session_obj.workshop_id)
    })


@observation_bp.route('/workshop/<int:workshop_id>/observations')
def view_observations(workshop_id):
    """Display consolidated observation table for a workshop."""
    from app.models.workshop import Workshop
    
    workshop = Workshop.query.get_or_404(workshop_id)
    
    # Get all observations for sessions in this workshop
    observations = db.session.query(ObservationalRecord).join(
        ObservationalRecord.session
    ).filter(
        Session.workshop_id == workshop_id
    ).order_by(ObservationalRecord.created_at.desc()).all()
    
    # Get all questions for table headers
    all_questions = get_all_questions()
    categories = OBSERVATION_CATEGORIES
    
    return render_template(
        'observation/table.html',
        workshop=workshop,
        observations=observations,
        all_questions=all_questions,
        categories=categories,
        answer_options=ANSWER_OPTIONS
    )
