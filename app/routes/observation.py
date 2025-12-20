"""Observation controller."""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session as flask_session
from flask_login import login_required, current_user

from app.services.observation_service import ObservationService
from app.models.observation_questions import (
    get_all_questions, get_question_by_index, get_total_question_count,
    ANSWER_OPTIONS, OBSERVATION_CATEGORIES
)

observation_bp = Blueprint('observation_bp', __name__)


@observation_bp.route('/session/<int:session_id>/observe/<int:participant_id>')
@login_required
def start_observation(session_id, participant_id):
    """Start the observational record flow."""
    # Use service to initialize observation
    observation_data, error = ObservationService.initialize_observation(
        session_id,
        participant_id,
        current_user.id
    )
    
    if error:
        # Get session to redirect to workshop
        from app.models.session import Session
        session_obj = Session.query.get(session_id)
        if session_obj:
            return redirect(url_for('workshop_bp.detail', workshop_id=session_obj.workshop_id))
        return redirect(url_for('workshop_bp.list_workshops'))
    
    # Store observation data in Flask session
    flask_session['observation_data'] = observation_data
    
    # Get session and participant for template
    from app.models.session import Session
    from app.models.participant import Participant
    session_obj = Session.query.get(session_id)
    participant = Participant.query.get(participant_id)
    
    # Get first question
    first_question = get_question_by_index(0)
    
    return render_template(
        'observation/create.html',
        session=session_obj,
        participant=participant,
        question=first_question,
        question_index=0,
        total_questions=get_total_question_count(),
        answer_options=ANSWER_OPTIONS,
        is_redo=observation_data['is_redo'],
        previous_answers=observation_data['answers']
    )


@observation_bp.route('/observation/answer', methods=['POST'])
@login_required
def process_answer():
    """Process an answer and move to the next question (AJAX)."""
    data = request.get_json()
    answer = data.get('answer')
    question_id = data.get('question_id')
    
    if 'observation_data' not in flask_session:
        return jsonify({'success': False, 'message': 'Sesión expirada'}), 400
    
    # Use service to process answer
    obs_data = flask_session['observation_data']
    obs_data = ObservationService.process_answer(obs_data, question_id, answer)
    
    if not obs_data:
        return jsonify({'success': False, 'message': 'Error procesando respuesta'}), 400
    
    # Update Flask session
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
            'message': 'Todas las preguntas respondidas'
        })


@observation_bp.route('/observation/complete', methods=['POST'])
@login_required
def complete_observation():
    """Save the completed observation with optional freeform notes."""
    if 'observation_data' not in flask_session:
        return jsonify({'success': False, 'message': 'Sesión expirada'}), 400
    
    data = request.get_json()
    freeform_notes = data.get('freeform_notes', '').strip()
    
    obs_data = flask_session['observation_data']
    
    # Use service to save observation
    record, error = ObservationService.save_observation(
        obs_data,
        freeform_notes,
        current_user.id
    )
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Clear session data
    flask_session.pop('observation_data', None)
    
    # Get workshop ID for redirect
    from app.models.session import Session
    session_obj = Session.query.get(obs_data['session_id'])
    
    return jsonify({
        'success': True,
        'message': 'Registro guardado exitosamente',
        'redirect_url': url_for('workshop_bp.detail', workshop_id=session_obj.workshop_id)
    })


@observation_bp.route('/workshop/<int:workshop_id>/observations')
@login_required
def view_observations(workshop_id):
    """Display consolidated observation table for a workshop."""
    # Use service to get observations
    observations, error = ObservationService.get_workshop_observations(
        workshop_id,
        current_user.id
    )
    
    if error:
        from flask import flash
        flash(error, 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
    
    # Get workshop for template
    from app.models.workshop import Workshop
    workshop = Workshop.query.get(workshop_id)
    
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
