"""Workshop controller."""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_babel import gettext as _
from app import db
from app.models.workshop import Workshop
from app.models.observation import ObservationalRecord

workshop_bp = Blueprint('workshop_bp', __name__)


@workshop_bp.route('/')
def list_workshops():
    """Display all workshops as cards on the main screen."""
    workshops = Workshop.query.order_by(Workshop.created_at.desc()).all()
    return render_template('workshop/list.html', workshops=workshops)


@workshop_bp.route('/workshop/create', methods=['POST'])
def create_workshop():
    """Create a new workshop."""
    name = request.form.get('name', '').strip()
    
    if not name:
        flash(_('El nombre del taller es obligatorio'), 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
    
    workshop = Workshop(name=name)
    db.session.add(workshop)
    db.session.commit()
    
    flash(_('Taller creado exitosamente'), 'success')
    return redirect(url_for('workshop_bp.detail', workshop_id=workshop.id))


@workshop_bp.route('/workshop/<int:workshop_id>')
def detail(workshop_id):
    """Display workshop detail view with participants, sessions, and objective."""
    workshop = Workshop.query.get_or_404(workshop_id)
    participants = workshop.participants.all()
    sessions = workshop.sessions.order_by('created_at').all()
    
    # Check if workshop has any observations
    has_observations = db.session.query(
        ObservationalRecord.query.join(ObservationalRecord.session).filter(
            db.session.query(db.literal(True)).filter(
                ObservationalRecord.session.has(workshop_id=workshop_id)
            ).exists()
        ).exists()
    ).scalar()
    
    return render_template(
        'workshop/detail.html',
        workshop=workshop,
        participants=participants,
        sessions=sessions,
        has_observations=has_observations
    )


@workshop_bp.route('/workshop/<int:workshop_id>/update-objective', methods=['POST'])
def update_objective(workshop_id):
    """Update workshop objective via AJAX."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    data = request.get_json()
    objective = data.get('objective', '').strip()
    
    workshop.objective = objective
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Objetivo actualizado'),
        'objective': objective
    })


@workshop_bp.route('/workshop/<int:workshop_id>/delete', methods=['POST', 'DELETE'])
def delete_workshop(workshop_id):
    """Delete a workshop and all related data."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    db.session.delete(workshop)
    db.session.commit()
    
    flash(_('Taller eliminado'), 'info')
    return redirect(url_for('workshop_bp.list_workshops'))
