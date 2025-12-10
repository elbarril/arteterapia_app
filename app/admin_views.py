"""Custom Flask-Admin views for the application."""
from flask import redirect, url_for, request, flash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from markupsafe import Markup
from wtforms import TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email
from app.utils.email_utils import send_invitation_email
import json


class SecureModelView(ModelView):
    """Base admin view with authentication check."""
    
    def is_accessible(self):
        """Only allow access to authenticated admin users."""
        return current_user.is_authenticated and current_user.is_admin()
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login if not authenticated, or home if not admin."""
        if current_user.is_authenticated:
            # User is logged in but not an admin, redirect to home
            flash('No tienes permiso para acceder al panel de administración.', 'danger')
            return redirect(url_for('workshop_bp.list_workshops'))
        # User is not logged in, redirect to login
        return redirect(url_for('auth_bp.login', next=request.url))


class WorkshopAdminView(SecureModelView):
    """Custom admin view for Workshop model."""
    
    column_list = ['id', 'name', 'objective', 'created_at']
    column_searchable_list = ['name', 'objective']
    column_filters = ['created_at']
    column_sortable_list = ['id', 'name', 'created_at']
    
    form_columns = ['name', 'objective']
    
    column_labels = {
        'id': 'ID',
        'name': 'Nombre',
        'objective': 'Objetivo',
        'created_at': 'Creado'
    }


class SessionAdminView(SecureModelView):
    """Custom admin view for Session model."""
    
    column_list = ['id', 'workshop_id', 'prompt', 'motivation', 'created_at']
    column_searchable_list = ['prompt', 'motivation']
    column_filters = ['workshop_id', 'created_at']
    column_sortable_list = ['id', 'workshop_id', 'created_at']
    
    # Display workshop name instead of ID
    column_formatters = {
        'workshop_id': lambda v, c, m, p: m.workshop.name if m.workshop else ''
    }
    
    # Explicitly include workshop_id in the form
    form_columns = ['workshop_id', 'prompt', 'motivation', 'materials']
    
    column_labels = {
        'id': 'ID',
        'workshop_id': 'Taller',
        'prompt': 'Consigna',
        'motivation': 'Motivación',
        'materials': 'Materiales',
        'created_at': 'Creado'
    }
    
    form_args = {
        'prompt': {
            'validators': [DataRequired()]
        },
        'workshop_id': {
            'validators': [DataRequired()]
        }
    }
    
    # Override form field for materials to use textarea
    form_overrides = {
        'materials': TextAreaField
    }
    
    def on_model_change(self, form, model, is_created):
        """Process materials field before saving."""
        if hasattr(form, 'materials') and form.materials.data:
            materials_text = form.materials.data.strip()
            if materials_text:
                try:
                    # Try to parse as JSON first
                    model.materials = json.loads(materials_text)
                except json.JSONDecodeError:
                    # If not valid JSON, treat as comma-separated list
                    model.materials = [m.strip() for m in materials_text.split(',') if m.strip()]
            else:
                model.materials = None
        else:
            model.materials = None
    
    def on_form_prefill(self, form, id):
        """Format materials field for display."""
        if hasattr(form, 'materials') and form.materials.data:
            if isinstance(form.materials.data, list):
                form.materials.data = ', '.join(form.materials.data)
            elif isinstance(form.materials.data, dict):
                form.materials.data = json.dumps(form.materials.data, ensure_ascii=False)


class ParticipantAdminView(SecureModelView):
    """Custom admin view for Participant model."""
    
    column_list = ['id', 'name', 'workshop_id', 'created_at']
    column_searchable_list = ['name']
    column_filters = ['workshop_id', 'created_at']
    column_sortable_list = ['id', 'name', 'workshop_id', 'created_at']
    
    # Display workshop name instead of ID
    column_formatters = {
        'workshop_id': lambda v, c, m, p: m.workshop.name if m.workshop else ''
    }
    
    # Explicitly include workshop_id in the form
    form_columns = ['name', 'workshop_id', 'extra_data']
    
    column_labels = {
        'id': 'ID',
        'name': 'Nombre',
        'workshop_id': 'Taller',
        'extra_data': 'Datos Adicionales',
        'created_at': 'Creado'
    }
    
    form_args = {
        'name': {
            'validators': [DataRequired()]
        },
        'workshop_id': {
            'validators': [DataRequired()]
        }
    }
    
    # Override form field for extra_data to use textarea
    form_overrides = {
        'extra_data': TextAreaField
    }
    
    def on_model_change(self, form, model, is_created):
        """Process extra_data field before saving."""
        if hasattr(form, 'extra_data') and form.extra_data.data:
            extra_data_text = form.extra_data.data.strip()
            if extra_data_text:
                try:
                    model.extra_data = json.loads(extra_data_text)
                except json.JSONDecodeError:
                    raise ValueError('Datos Adicionales debe ser JSON válido (ej: {"edad": 30, "contacto": "email@example.com"})')
            else:
                model.extra_data = None
        else:
            model.extra_data = None
    
    def on_form_prefill(self, form, id):
        """Format extra_data field for display."""
        if hasattr(form, 'extra_data') and form.extra_data.data:
            form.extra_data.data = json.dumps(form.extra_data.data, ensure_ascii=False, indent=2)


class ObservationalRecordAdminView(SecureModelView):
    """Custom admin view for ObservationalRecord model."""
    
    column_list = ['id', 'session_id', 'participant_id', 'freeform_notes', 'created_at']
    column_searchable_list = ['freeform_notes']
    column_filters = ['session_id', 'participant_id', 'created_at']
    column_sortable_list = ['id', 'session_id', 'participant_id', 'created_at']
    
    # Display session and participant info instead of IDs
    column_formatters = {
        'session_id': lambda v, c, m, p: f"Session {m.session.id}: {m.session.prompt[:30]}..." if m.session else '',
        'participant_id': lambda v, c, m, p: m.participant.name if m.participant else ''
    }
    
    # Explicitly include session_id and participant_id in the form
    form_columns = ['session_id', 'participant_id', 'answers', 'freeform_notes']
    
    column_labels = {
        'id': 'ID',
        'session_id': 'Sesión',
        'participant_id': 'Participante',
        'answers': 'Respuestas',
        'freeform_notes': 'Notas',
        'created_at': 'Creado'
    }
    
    form_args = {
        'session_id': {
            'validators': [DataRequired()]
        },
        'participant_id': {
            'validators': [DataRequired()]
        }
    }
    
    # Override form field for answers to use textarea
    form_overrides = {
        'answers': TextAreaField,
        'freeform_notes': TextAreaField
    }
    
    def on_model_change(self, form, model, is_created):
        """Process answers field before saving."""
        if hasattr(form, 'answers') and form.answers.data:
            answers_text = form.answers.data.strip()
            if answers_text:
                try:
                    model.answers = json.loads(answers_text)
                except json.JSONDecodeError:
                    raise ValueError('Respuestas debe ser JSON válido (ej: {"entry_on_time": "yes", "entry_resistance": "no"})')
            else:
                model.answers = {}
        else:
            model.answers = {}
    
    def on_form_prefill(self, form, id):
        """Format answers field for display."""
        if hasattr(form, 'answers') and form.answers.data:
            form.answers.data = json.dumps(form.answers.data, ensure_ascii=False, indent=2)


class UserAdminView(SecureModelView):
    """Custom admin view for User model."""
    
    column_list = ['id', 'username', 'email', 'email_verified', 'active', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['active', 'email_verified', 'created_at']
    column_sortable_list = ['id', 'username', 'email', 'created_at']
    
    # Don't show password hash in list
    column_exclude_list = ['password_hash', 'verification_token', 'reset_token', 'reset_token_expiry']
    
    # Don't allow editing password hash directly
    form_excluded_columns = ['password_hash', 'verification_token', 'reset_token', 'reset_token_expiry', 'invitations_created']
    
    column_labels = {
        'id': 'ID',
        'username': 'Usuario',
        'email': 'Correo',
        'active': 'Activo',
        'email_verified': 'Email Verificado',
        'must_change_password': 'Debe Cambiar Contraseña',
        'created_at': 'Creado',
        'roles': 'Roles'
    }
    
    # Format boolean columns
    column_formatters = {
        'email_verified': lambda v, c, m, p: '✓' if m.email_verified else '✗',
        'active': lambda v, c, m, p: '✓' if m.active else '✗',
    }
    
    form_args = {
        'username': {
            'validators': [DataRequired()]
        },
        'email': {
            'validators': [DataRequired(), Email()]
        }
    }


class RoleAdminView(SecureModelView):
    """Custom admin view for Role model."""
    
    column_list = ['id', 'name', 'description', 'created_at']
    column_searchable_list = ['name', 'description']
    column_sortable_list = ['id', 'name', 'created_at']
    
    column_labels = {
        'id': 'ID',
        'name': 'Nombre',
        'description': 'Descripción',
        'created_at': 'Creado'
    }
    
    form_args = {
        'name': {
            'validators': [DataRequired()]
        }
    }


class UserInvitationAdminView(SecureModelView):
    """Custom admin view for UserInvitation model."""
    
    column_list = ['id', 'email', 'status', 'registration_url', 'created_by_user_id', 'created_at', 'expires_at', 'used_at']
    column_searchable_list = ['email']
    column_filters = ['created_at', 'expires_at', 'used_at']
    column_sortable_list = ['id', 'email', 'created_at', 'expires_at']
    
    # Don't allow editing token directly
    form_excluded_columns = ['token', 'used_at', 'created_by_user_id']
    
    # Only show email field on create, everything else is auto-generated
    form_create_rules = ['email']
    
    # On edit, show all non-excluded fields as read-only except email
    form_edit_rules = ['email', 'created_at', 'expires_at']
    
    # Make fields read-only in edit form
    form_widget_args = {
        'created_at': {'readonly': True},
        'expires_at': {'readonly': True}
    }
    
    column_labels = {
        'id': 'ID',
        'email': 'Correo',
        'status': 'Estado',
        'registration_url': 'URL de Registro',
        'created_by_user_id': 'Creado Por',
        'created_at': 'Creado',
        'expires_at': 'Expira',
        'used_at': 'Usado'
    }
    
    # Format columns
    column_formatters = {
        'created_by_user_id': lambda v, c, m, p: m.creator.username if m.creator else '',
        'status': lambda v, c, m, p: {
            'pending': '⏳ Pendiente',
            'used': '✓ Usado',
            'expired': '✗ Expirado'
        }.get(m.status, m.status),
        'registration_url': lambda v, c, m, p: Markup(f'<a href="/register/{m.token}" target="_blank">/register/{m.token[:8]}...</a>') if m.token else ''
    }
    
    form_args = {
        'email': {
            'validators': [DataRequired(), Email()]
        }
    }
    
    def on_model_change(self, form, model, is_created):
        """Send invitation email when creating new invitation."""
        if is_created:
            from flask_login import current_user
            from flask import current_app
            from datetime import datetime, timedelta
            from app import db
            import secrets
            
            # Set created_by to current user
            model.created_by_user_id = current_user.id
            
            # Generate token if not set
            if not model.token:
                model.token = secrets.token_urlsafe(32)
            
            # Set expiry if not set (7 days from now)
            if not model.expires_at:
                expiry_days = current_app.config.get('INVITATION_EXPIRY_DAYS', 7)
                model.expires_at = datetime.utcnow() + timedelta(days=expiry_days)
            
            # Send invitation email after commit
            db.session.flush()
            send_invitation_email(model)


