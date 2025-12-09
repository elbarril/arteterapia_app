"""Workshop controller."""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_babel import gettext as _
from flask_login import login_required, current_user
from app import db
from app.models.workshop import Workshop
from app.models.observation import ObservationalRecord

workshop_bp = Blueprint('workshop_bp', __name__)


@workshop_bp.route('/')
@login_required
def list_workshops():
    """List all workshops owned by the current user."""
    # Only show workshops owned by current user (admins see all)
    if current_user.is_admin():
        workshops = Workshop.query.order_by(Workshop.created_at.desc()).all()
    else:
        workshops = Workshop.query.filter_by(user_id=current_user.id).order_by(Workshop.created_at.desc()).all()
    return render_template('workshop/list.html', workshops=workshops)


@workshop_bp.route('/workshop/create', methods=['POST'])
@login_required
def create_workshop():
    """Create a new workshop."""
    name = request.form.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'message': _('El nombre es requerido')}), 400
    
    # Create workshop owned by current user
    workshop = Workshop(name=name, user_id=current_user.id)
    db.session.add(workshop)
    db.session.commit()
    
    flash(_('Taller creado exitosamente'), 'success')
    return redirect(url_for('workshop_bp.detail', workshop_id=workshop.id))


@workshop_bp.route('/<int:workshop_id>')
@login_required
def detail(workshop_id):
    """Show workshop details."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    # Check if user owns this workshop (admins can access all)
    if not current_user.is_admin() and workshop.user_id != current_user.id:
        flash(_('No tienes permiso para acceder a este taller'), 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
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


@workshop_bp.route('/<int:workshop_id>/objective', methods=['POST'])
@login_required
def update_objective(workshop_id):
    """Update workshop objective."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    # Check ownership
    if not current_user.is_admin() and workshop.user_id != current_user.id:
        return jsonify({'success': False, 'message': _('No tienes permiso')}), 403
    
    data = request.get_json()
    objective = data.get('objective', '').strip()
    
    workshop.objective = objective
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Objetivo actualizado'),
        'objective': objective
    })


@workshop_bp.route('/<int:workshop_id>/delete', methods=['POST'])
@login_required
def delete_workshop(workshop_id):
    """Delete a workshop."""
    workshop = Workshop.query.get_or_404(workshop_id)
    
    # Check ownership
    if not current_user.is_admin() and workshop.user_id != current_user.id:
        flash(_('No tienes permiso para eliminar este taller'), 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
    
    db.session.delete(workshop)
    db.session.commit()
    
    flash(_('Taller eliminado'), 'info')
    return redirect(url_for('workshop_bp.list_workshops'))
