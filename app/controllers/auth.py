"""Authentication controller."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext as _
from app import db
from app.models.user import User
from app.models.user_invitation import UserInvitation
from app.utils.email_utils import send_verification_email, send_password_reset_email
import re

auth_bp = Blueprint('auth_bp', __name__)


def validate_password_strength(password):
    """Validate password meets minimum requirements."""
    if len(password) < 8:
        return False, _('La contraseña debe tener al menos 8 caracteres')
    if not re.search(r'[A-Za-z]', password):
        return False, _('La contraseña debe contener al menos una letra')
    if not re.search(r'\d', password):
        return False, _('La contraseña debe contener al menos un número')
    return True, None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('workshop_bp.list_workshops'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        if not username_or_email or not password:
            flash(_('Por favor completa todos los campos'), 'danger')
            return render_template('auth/login.html')
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            flash(_('Usuario o contraseña incorrectos'), 'danger')
            return render_template('auth/login.html')
        
        if not user.active:
            flash(_('Tu cuenta ha sido desactivada'), 'danger')
            return render_template('auth/login.html')
        
        if not user.email_verified:
            flash(_('Por favor verifica tu correo electrónico antes de iniciar sesión'), 'warning')
            return render_template('auth/login.html')
        
        # Login successful
        login_user(user, remember=remember)
        
        # Check if password must be changed
        if user.must_change_password:
            flash(_('Debes cambiar tu contraseña antes de continuar'), 'warning')
            return redirect(url_for('auth_bp.change_password', force=True))
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('workshop_bp.list_workshops'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash(_('Has cerrado sesión exitosamente'), 'info')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    """User registration via invitation token."""
    # Validate invitation token
    invitation = UserInvitation.query.filter_by(token=token).first()
    
    if not invitation:
        flash(_('Invitación no válida'), 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if not invitation.is_valid():
        flash(_('Esta invitación ha expirado o ya fue utilizada'), 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validation
        if not username or not password:
            flash(_('Por favor completa todos los campos'), 'danger')
            return render_template('auth/register.html', invitation=invitation)
        
        if password != password_confirm:
            flash(_('Las contraseñas no coinciden'), 'danger')
            return render_template('auth/register.html', invitation=invitation)
        
        # Validate password strength
        valid, error_msg = validate_password_strength(password)
        if not valid:
            flash(error_msg, 'danger')
            return render_template('auth/register.html', invitation=invitation)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash(_('Este nombre de usuario ya está en uso'), 'danger')
            return render_template('auth/register.html', invitation=invitation)
        
        # Check if email already exists
        if User.query.filter_by(email=invitation.email).first():
            flash(_('Este correo electrónico ya está registrado'), 'danger')
            return render_template('auth/register.html', invitation=invitation)
        
        # Create new user
        user = User(
            username=username,
            email=invitation.email,
            active=True,
            email_verified=False
        )
        user.set_password(password)
        user.generate_verification_token()
        
        db.session.add(user)
        
        # Mark invitation as used
        invitation.mark_as_used()
        
        db.session.commit()
        
        # Send verification email
        send_verification_email(user)
        
        # Log out current user if any (e.g., admin who created the invitation)
        if current_user.is_authenticated:
            logout_user()
        
        flash(_('Cuenta creada exitosamente. Por favor verifica tu correo electrónico.'), 'success')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/register.html', invitation=invitation)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user email address."""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash(_('Token de verificación no válido'), 'danger')
        return redirect(url_for('auth_bp.login'))
    
    user.verify_email()
    db.session.commit()
    
    flash(_('¡Correo electrónico verificado exitosamente! Ya puedes iniciar sesión.'), 'success')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('workshop_bp.list_workshops'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash(_('Por favor ingresa tu correo electrónico'), 'danger')
            return render_template('auth/forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message to prevent email enumeration
        if user and user.active:
            user.generate_reset_token()
            db.session.commit()
            send_password_reset_email(user)
        
        flash(_('Si el correo existe, recibirás instrucciones para restablecer tu contraseña'), 'info')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('workshop_bp.list_workshops'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash(_('Token de restablecimiento no válido o expirado'), 'danger')
        return redirect(url_for('auth_bp.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if not password:
            flash(_('Por favor ingresa una contraseña'), 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        if password != password_confirm:
            flash(_('Las contraseñas no coinciden'), 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # Validate password strength
        valid, error_msg = validate_password_strength(password)
        if not valid:
            flash(error_msg, 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # Update password
        user.set_password(password)
        user.clear_reset_token()
        user.must_change_password = False
        db.session.commit()
        
        flash(_('Contraseña restablecida exitosamente'), 'success')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user."""
    force = request.args.get('force', False)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        new_password_confirm = request.form.get('new_password_confirm', '')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash(_('Contraseña actual incorrecta'), 'danger')
            return render_template('auth/change_password.html', force=force)
        
        if not new_password:
            flash(_('Por favor ingresa una nueva contraseña'), 'danger')
            return render_template('auth/change_password.html', force=force)
        
        if new_password != new_password_confirm:
            flash(_('Las contraseñas nuevas no coinciden'), 'danger')
            return render_template('auth/change_password.html', force=force)
        
        # Validate password strength
        valid, error_msg = validate_password_strength(new_password)
        if not valid:
            flash(error_msg, 'danger')
            return render_template('auth/change_password.html', force=force)
        
        # Update password
        current_user.set_password(new_password)
        current_user.must_change_password = False
        db.session.commit()
        
        flash(_('Contraseña cambiada exitosamente'), 'success')
        return redirect(url_for('workshop_bp.list_workshops'))
    
    return render_template('auth/change_password.html', force=force)
